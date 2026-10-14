from .arithmetic import Arithmetic
from .block_design import BlockDesign
from .digit_span import DigitSpan
from .matrix_reasoning import MatrixReasoning
from .speed import Coding, SymbolSearch
from .verbal import Information, Similarities, Vocabulary
from .visual_puzzles import VisualPuzzles

# WAIS-IV core administration order
ORDER = [BlockDesign, Similarities, DigitSpan, MatrixReasoning, Vocabulary, Arithmetic, SymbolSearch, VisualPuzzles,
         Information, Coding]
BY_CODE = {cls.code: cls for cls in ORDER}
