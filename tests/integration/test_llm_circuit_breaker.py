"""
Integration tests for LLM service circuit breaker.

Tests circuit breaker behavior with realistic failure scenarios:
- Transient network failures
- Sustained outages
- Recovery after downtime
- Retry logic with exponential backoff
"""

import pytest
import httpx
import time
from unittest.mock import AsyncMock, Mock, patch
from apps.api.services.llm_service import LLMService, CircuitState


class TestLLMCircuitBreakerIntegration:
    """Integration tests for circuit breaker with retry logic."""

    @pytest.mark.asyncio
    async def test_transient_failure_recovers_with_retry(self):
        """Test that transient failures are handled by retry logic."""
        mock_client = AsyncMock()
        call_count = [0]

        async def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 2:
                # First 2 calls fail (will be retried)
                raise httpx.TimeoutException("Timeout")
            # Third call succeeds
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Recovered response"}}]
            }
            mock_response.raise_for_status = Mock()
            return mock_response

        mock_client.post.side_effect = side_effect

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            result = await service.chat_completion(messages)

            # Should succeed after retries
            assert result == "Recovered response"
            assert call_count[0] == 3  # 2 failures + 1 success
            assert service.circuit_breaker.success_count == 1
            assert service.circuit_breaker.failure_count == 0  # Reset on success
            assert service.circuit_breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_sustained_failures_open_circuit(self):
        """Test that sustained failures open the circuit breaker."""
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.ConnectError("Connection refused")

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            # Make 5 requests (each will retry 3 times internally)
            for i in range(5):
                result = await service.chat_completion(messages)
                assert "[LLM unavailable:" in result
                assert service.circuit_breaker.failure_count == i + 1

            # Circuit should now be open
            assert service.circuit_breaker.state == CircuitState.OPEN

            # Verify subsequent requests are rejected without hitting the LLM
            mock_client.post.reset_mock()
            result = await service.chat_completion(messages)

            assert "[LLM unavailable - circuit breaker open:" in result
            mock_client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_circuit_recovers_after_timeout(self):
        """Test that circuit recovers to half-open after recovery timeout."""
        mock_client = AsyncMock()
        call_count = [0]

        async def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] <= 15:  # 5 requests × 3 retries = 15 failures
                raise httpx.HTTPError("Service unavailable")
            # After recovery timeout, succeed
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Service restored"}}]
            }
            mock_response.raise_for_status = Mock()
            return mock_response

        mock_client.post.side_effect = side_effect

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = LLMService()
            # Set short recovery timeout for testing
            service.circuit_breaker.recovery_timeout = 1

            messages = [{"role": "user", "content": "Test"}]

            # Open the circuit with failures
            for _ in range(5):
                await service.chat_completion(messages)

            assert service.circuit_breaker.state == CircuitState.OPEN

            # Wait for recovery timeout
            time.sleep(1.1)

            # Next request should attempt (half-open) and succeed
            result = await service.chat_completion(messages)

            assert result == "Service restored"
            assert service.circuit_breaker.state == CircuitState.CLOSED
            assert service.circuit_breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_mixed_success_and_failure_scenarios(self):
        """Test circuit behavior with mixed success/failure patterns."""
        mock_client = AsyncMock()
        
        # Track which request we're on
        request_count = [0]
        
        async def side_effect(*args, **kwargs):
            # Request 1: Success
            if request_count[0] == 0:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": "Response 1"}}]
                }
                mock_response.raise_for_status = Mock()
                return mock_response
            # Request 2: Success
            elif request_count[0] == 1:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": "Response 2"}}]
                }
                mock_response.raise_for_status = Mock()
                return mock_response
            # Request 3: All attempts fail (retries 3 times)
            elif request_count[0] == 2:
                raise httpx.HTTPError("Error 1")
            # Request 4: Success (resets counter)
            elif request_count[0] == 3:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": "Response 3"}}]
                }
                mock_response.raise_for_status = Mock()
                return mock_response
            else:
                raise httpx.HTTPError("Out of responses")

        mock_client.post.side_effect = side_effect

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            # First success
            result = await service.chat_completion(messages)
            request_count[0] += 1
            assert result == "Response 1"
            assert service.circuit_breaker.state == CircuitState.CLOSED

            # Second success
            result = await service.chat_completion(messages)
            request_count[0] += 1
            assert result == "Response 2"
            assert service.circuit_breaker.success_count == 2
            assert service.circuit_breaker.failure_count == 0

            # Failure (retries 3 times, all fail)
            result = await service.chat_completion(messages)
            request_count[0] += 1
            assert "[LLM unavailable:" in result
            assert service.circuit_breaker.failure_count == 1

            # Success resets failure count
            result = await service.chat_completion(messages)
            request_count[0] += 1
            assert result == "Response 3"
            assert service.circuit_breaker.failure_count == 0

    @pytest.mark.asyncio
    async def test_retry_timing_with_exponential_backoff(self):
        """Test that retries use exponential backoff (1s, 2s, 4s)."""
        mock_client = AsyncMock()
        call_times = []

        async def side_effect(*args, **kwargs):
            call_times.append(time.time())
            # Always fail to trigger all retries
            raise httpx.TimeoutException("Timeout")

        mock_client.post.side_effect = side_effect

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            start_time = time.time()
            await service.chat_completion(messages)

            # Should have made 3 attempts (initial + 2 retries)
            assert len(call_times) == 3

            # Verify backoff timing (allow 0.5s tolerance)
            # Initial call: ~0s
            # Retry 1: ~1s after initial
            # Retry 2: ~3s after initial (1s + 2s)
            assert call_times[0] - start_time < 0.5
            assert 0.5 < call_times[1] - call_times[0] < 1.5  # ~1s wait
            assert 1.5 < call_times[2] - call_times[1] < 2.5  # ~2s wait

            # Total time should be ~3s (1s + 2s backoff)
            total_time = time.time() - start_time
            assert 2.5 < total_time < 4.0

    @pytest.mark.asyncio
    async def test_partial_failures_dont_open_circuit(self):
        """Test that failures below threshold don't open circuit."""
        mock_client = AsyncMock()
        failure_count = [0]

        async def side_effect(*args, **kwargs):
            failure_count[0] += 1
            # Fail 3 times (below threshold of 5)
            if failure_count[0] <= 9:  # 3 requests × 3 retries
                raise httpx.HTTPError("Error")
            # Then succeed
            mock_response = Mock()
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Success"}}]
            }
            mock_response.raise_for_status = Mock()
            return mock_response

        mock_client.post.side_effect = side_effect

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            # 3 failures (below threshold)
            for _ in range(3):
                result = await service.chat_completion(messages)
                assert "[LLM unavailable:" in result

            # Circuit should still be closed
            assert service.circuit_breaker.state == CircuitState.CLOSED
            assert service.circuit_breaker.failure_count == 3

            # Success resets counter
            result = await service.chat_completion(messages)
            assert result == "Success"
            assert service.circuit_breaker.failure_count == 0


class TestLLMCircuitBreakerMetrics:
    """Test circuit breaker metrics tracking."""

    @pytest.mark.asyncio
    async def test_metrics_track_success_and_failure_counts(self):
        """Test that metrics accurately track success and failure counts."""
        mock_client = AsyncMock()
        request_num = [0]  # Track which high-level request we're on

        async def side_effect(*args, **kwargs):
            # Each request can have multiple attempts due to retries
            # We want: success, fail (all retries), success, fail (all retries), success
            if request_num[0] in [0, 2, 4]:  # Successes on requests 0, 2, 4
                mock_response = Mock()
                mock_response.json.return_value = {
                    "choices": [{"message": {"content": f"Response {request_num[0] + 1}"}}]
                }
                mock_response.raise_for_status = Mock()
                return mock_response
            else:  # Failures on requests 1, 3 (will retry 3 times each)
                raise httpx.HTTPError("Error")

        mock_client.post.side_effect = side_effect

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            # Request 0: success
            result = await service.chat_completion(messages)
            assert "Response 1" in result
            request_num[0] += 1

            # Request 1: fail (all 3 retry attempts)
            result = await service.chat_completion(messages)
            assert "[LLM unavailable:" in result
            request_num[0] += 1

            # Request 2: success (resets failure count)
            result = await service.chat_completion(messages)
            assert "Response 3" in result
            request_num[0] += 1

            # Request 3: fail (all 3 retry attempts)
            result = await service.chat_completion(messages)
            assert "[LLM unavailable:" in result
            request_num[0] += 1

            # Request 4: success (resets failure count again)
            result = await service.chat_completion(messages)
            assert "Response 5" in result
            request_num[0] += 1

            metrics = service.get_circuit_breaker_metrics()

            # Should have 3 successes (requests 0, 2, 4)
            assert metrics["success_count"] == 3
            # Failure count resets after each success
            assert metrics["failure_count"] == 0  # Reset by last success
            assert metrics["state"] == "closed"

    @pytest.mark.asyncio
    async def test_metrics_track_timestamps(self):
        """Test that metrics track last success and failure times."""
        mock_client = AsyncMock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Success"}}]
        }
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_client):
            service = LLMService()
            messages = [{"role": "user", "content": "Test"}]

            before = time.time()
            await service.chat_completion(messages)
            after = time.time()

            metrics = service.get_circuit_breaker_metrics()

            assert metrics["last_success_time"] is not None
            assert before <= metrics["last_success_time"] <= after
            assert metrics["last_failure_time"] is None  # No failures yet

    def test_metrics_expose_circuit_configuration(self):
        """Test that metrics include circuit breaker configuration."""
        service = LLMService()
        metrics = service.get_circuit_breaker_metrics()

        assert metrics["failure_threshold"] == 5
        assert metrics["recovery_timeout"] == 60
        assert "state" in metrics
        assert "failure_count" in metrics
        assert "success_count" in metrics
