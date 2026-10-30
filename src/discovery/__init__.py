"""Mathematical discovery algorithms package."""

from .base import DiscoveryMethod
from .finite_differences import FiniteDifferenceDiscovery
from .quasipolynomial import QuasipolynomialDiscovery
from .linear_recurrence import LinearRecurrenceDiscovery
from .inhomogeneous import InhomogeneousRecurrenceDiscovery
from .holonomic import HolonomicDiscovery
from .nonlinear import NonlinearRecurrenceDiscovery
from .algebraic_gf import AlgebraicGeneratingFunctionDiscovery
from .convolution import ConvolutionRecurrenceDiscovery
from .multiplicative import MultiplicativeRecurrenceDiscovery
from .generating_function import GeneratingFunctionDiscovery
from .symbolic_search import SymbolicExpressionDiscovery
from .transforms import TransformDiscovery
from .modular import ModularPatternDiscovery
from .asymptotic import AsymptoticGrowthDiscovery

__all__ = [
    "DiscoveryMethod",
    "FiniteDifferenceDiscovery",
    "QuasipolynomialDiscovery",
    "LinearRecurrenceDiscovery",
    "InhomogeneousRecurrenceDiscovery",
    "HolonomicDiscovery",
    "NonlinearRecurrenceDiscovery",
    "AlgebraicGeneratingFunctionDiscovery",
    "ConvolutionRecurrenceDiscovery",
    "MultiplicativeRecurrenceDiscovery",
    "GeneratingFunctionDiscovery",
    "SymbolicExpressionDiscovery",
    "TransformDiscovery",
    "ModularPatternDiscovery",
    "AsymptoticGrowthDiscovery",
]
