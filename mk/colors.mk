# =============================================================================
# COLORES Y EMOJIS PARA MAKEFILE
# =============================================================================

# Colores
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m  # No Color

# Emojis
EMOJI_INFO = ℹ️
EMOJI_CHECK = ✅
EMOJI_ERROR = ❌
EMOJI_WARN = ⚠️

# Función para logging
define log_info
    @echo "$(BLUE)$(EMOJI_INFO) $(1)$(NC)"
endef

define log_success
    @echo "$(GREEN)$(EMOJI_CHECK) $(1)$(NC)"
endef

define log_error
    @echo "$(RED)$(EMOJI_ERROR) $(1)$(NC)" && exit 1
endef

define log_warn
    @echo "$(YELLOW)$(EMOJI_WARN) $(1)$(NC)"
endef
