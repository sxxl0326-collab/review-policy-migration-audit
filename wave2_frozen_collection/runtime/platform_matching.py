"""In-memory correction: CodeOwners 0.9 masks filename spaces with slashes,
which prevents a slash-excluding wildcard matching a real filename space.
Keep pinned upstream files unchanged; use one non-slash sentinel instead.
Case-sensitive matching and original input text are preserved.
"""
import run_controls
import codeowners
def activate():
 codeowners.MASK='\uE000'
