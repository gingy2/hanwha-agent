class AgentError(Exception):
    status_code = 400
    code = "agent_error"  

    def __init__(self, message: str, *, detail: str | None = None):
        super().__init__(message)  # print(e) -> 메세지 나옴 
        self.message = message 
        self.detail = detail 
 
# 요청한 자원이 없다
class NotFound(AgentError):
    status_code=404
    code='not found'

# 자원은 있으나 이 사용자가 접근할 수 없다
class PermissionDenied(AgentError):
    status_code=403
    code='permission_denied'

# 입력값이 규칙에 맞지 않다
class ValidationFailed(AgentError):
    status_code=422
    code='validation_failed'

# 입력 가드에 걸림 - 길이 초과, 인젝션 의심 등
class GuardTripped(AgentError):
    status_code=400
    code='guard_tripped'

# 호출 한도 초과
class RateLimited(AgentError):
    status_code=429
    code='rate_limited'

# 승인 없이 외부 실행 시도
class ApprovalRequired(AgentError):
    status_code=409
    code='approval_required'

# 모드 변경 불가 시
class ModeNotAvailable(AgentError):
    status_code = 409
    code = "mode_not_available"

# 외부 서비스 호출 실패
class ExternalServiceError(AgentError):
    status_code=502
    code='external_service_error'

e=NotFound('문서를 찾을 수 없습니다.', detail='doc_id에 id가 없음')