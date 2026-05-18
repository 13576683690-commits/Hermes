from prover.lean.verifier import verify_lean4_file

code = '''import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

theorem test_
(x:ℝ)
(y:ℝ)
(h1: x^2=x^4)
:
x^4=x^2 := by sorry
'''

code = '''import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat


lemma test:
  ¬(2 + 2 = 5) := by
  push_neg ; sorry'''

result = verify_lean4_file(code, timeout=30)

print(result)