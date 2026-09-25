"""개인용 설정. .env 파일 없이 실행합니다."""

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
MODEL_ID = "google/gemma-4-31B-it"
# 다른 로컬 모델 스냅샷을 쓰려면 절대 경로를 지정합니다. None이면 HF 캐시에서 찾습니다.
MODEL_PATH: Path | None = None
SHARED_HF_HOME = Path("/home/shared/hf_cache")
MIN_FREE_GPU_MIB = 20 * 1024  # GPU별 여유분을 제외한 합산 모델 로딩 예산
GPU_MEMORY_RESERVE_MIB = 2 * 1024  # GPU마다 CUDA 커널·KV 캐시·출력용으로 남길 공간
LLM_TIMEOUT_SECONDS = 240
MCP_URL = "https://evalstate-flux1-schnell.hf.space/gradio_api/mcp/sse"
MCP_TOOL = "flux1_schnell_infer"
MCP_TIMEOUT_SECONDS = 180
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

FONT_KOREAN = PROJECT_DIR / "fonts" / "NotoSansKR-VF.ttf"
