# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Linear algebra submodule"""
from .. import numpy as mnp
from .. import ops
from .ops import SolveTriangular
from .ops import CholeskySolver
from .ops import Cholesky
from .ops import LU
from .ops import LUSolver
from .ops import EighNet
from ..ops import operations as P
from ..ops import functional as F
from ..common import dtype as mstype
from .utils import float_types
from .utils_const import _raise_value_error

__all__ = ['block_diag', 'inv', 'eigh', 'lu_factor', 'lu']


def block_diag(*arrs):
    """
    Create a block diagonal matrix from provided arrays.

    Given the list of Tensors `A`, `B`, and `C`, the output will have these
    Tensors arranged on the diagonal:

    .. code-block::

        [[A, 0, 0],
         [0, B, 0],
         [0, 0, C]]

    Args:
        arrs (list): up to 2-D Input Tensors.
            A 1-D Tensor or a 2-D Tensor with shape :math:`(1,n)`.

    Returns:
        Tensor with `A`, `B`, `C`, ... on the diagonal which has the same dtype as `A`.

    Raises:
        ValueError: If there are Tensors with dimensions higher than 2 in all arguments.

    Supported Platforms:
        ``CPU`` ``GPU``

    Examples:
        >>> import numpy as onp
        >>> from mindspore.common import Tensor
        >>> from mindspore.scipy.linalg import block_diag
        >>> A = Tensor(onp.array([[1, 0], [0, 1]]))
        >>> B = Tensor(onp.array([[3, 4, 5], [6, 7, 8]]))
        >>> C = Tensor(onp.array([[7]]))
        >>> P = Tensor(onp.zeros((2, ), dtype='int32'))
        >>> block_diag(A, B, C)
        Tensor(shape=[5, 6], dtype=Int64, value=
        [[1, 0, 0, 0, 0, 0],
         [0, 1, 0, 0, 0, 0],
         [0, 0, 3, 4, 5, 0],
         [0, 0, 6, 7, 8, 0],
         [0, 0, 0, 0, 0, 7]])
        >>> block_diag(A, P, B, C)
        Tensor(shape=[6, 8], dtype=Int64, value=
        [[1, 0, 0 ... 0, 0, 0],
         [0, 1, 0 ... 0, 0, 0],
         [0, 0, 0 ... 0, 0, 0],
         [0, 0, 0 ... 4, 5, 0],
         [0, 0, 0 ... 7, 8, 0],
         [0, 0, 0 ... 0, 0, 7]])
    """
    if not arrs:
        return mnp.zeros((1, 0))
    bad_shapes = [i for i, a in enumerate(arrs) if a.ndim > 2]
    if bad_shapes:
        _raise_value_error("Arguments to mindspore.scipy.linalg.block_diag must have at most 2 dimensions.")

    accum = mnp.atleast_2d(arrs[0])
    for arr in arrs[1:]:
        arr = mnp.atleast_2d(arr)
        _, c = arr.shape
        arr = ops.Pad(((0, 0), (accum.shape[-1], 0)))(arr)
        accum = ops.Pad(((0, 0), (0, c)))(accum)
        accum = mnp.concatenate([accum, arr], axis=0)
    return accum


def solve_triangular(A, b, trans=0, lower=False, unit_diagonal=False,
                     overwrite_b=False, debug=None, check_finite=True):
    """
    Solve the equation `a x = b` for `x`, assuming a is a triangular matrix.

    Args:
        A (Tensor): A triangular matrix of shape :math:`(N, N)`.
        b (Tensor): A Tensor of shape :math:`(M,)` or :math:`(M, N)`.
            Right-hand side matrix in :math:`A x = b`.
        lower (bool, optional): Use only data contained in the lower triangle of `a`.
            Default is to use upper triangle.
        trans (0, 1, 2, 'N', 'T', 'C', optional):
            Type of system to solve:
            trans:        system:
                0 or 'N'        a x  = b
                1 or 'T'        a^T x = b
                2 or 'C'        a^H x = b
        unit_diagonal (bool, optional): If True, diagonal elements of :math:`A` are assumed to be 1 and
            will not be referenced.
        overwrite_b (bool, optional): Allow overwriting data in :math:`b` (may enhance performance)
        check_finite (bool, optional): Whether to check that the input matrices contain only finite numbers.
            Disabling may give a performance gain, but may result in problems
            (crashes, non-termination) if the inputs do contain infinities or NaNs.

    Returns:
        Tensor of shape :math:`(M,)` or :math:`(M, N)`,
        which is the solution to the system :math:`A x = b`.
        Shape of :math:`x` matches :math:`b`.

    Raises:
        LinAlgError: If :math:`A` is singular

    Supported Platforms:
        ``CPU`` ``GPU``

    Examples:
        Solve the lower triangular system :math:`A x = b`, where:

                 [3  0  0  0]       [4]
            A =  [2  1  0  0]   b = [2]
                 [1  0  1  0]       [4]
                 [1  1  1  1]       [2]

        >>> import numpy as onp
        >>> from mindspore.common import Tensor
        >>> import mindspore.numpy as mnp
        >>> from mindspore.scipy.linalg import solve_triangular
        >>> A = Tensor(onp.array([[3, 0, 0, 0], [2, 1, 0, 0], [1, 0, 1, 0], [1, 1, 1, 1]], onp.float64))
        >>> b = Tensor(onp.array([4, 2, 4, 2], onp.float64))
        >>> x = solve_triangular(A, b, lower=True, unit_diagonal=False, trans='N')
        >>> x
        Tensor(shape=[4], dtype=Float32, value= [ 1.33333337e+00, -6.66666746e-01,  2.66666651e+00, -1.33333313e+00])
        >>> mnp.dot(A, x)  # Check the result
        Tensor(shape=[4], dtype=Float32, value= [ 4.00000000e+00,  2.00000000e+00,  4.00000000e+00,  2.00000000e+00])
    """
    if isinstance(trans, int):
        trans_table = ['N', 'T', 'C']
        trans = trans_table[trans]
    solve = SolveTriangular(lower, unit_diagonal, trans)
    return solve(A, b)


def inv(a, overwrite_a=False, check_finite=True):
    """
    Compute the inverse of a matrix.

    Args:
        a (Tensor): Square matrix to be inverted. Note that if the input tensor is not a `float`,
        then it will be casted to :class:`mstype.float32`.
        overwrite_a (bool, optional): Discard data in `a` (may improve performance). Default: False.
        check_finite (bool, optional): Whether to check that the input matrix contains only finite numbers.
            Disabling may give a performance gain, but may result in problems (crashes, non-termination)
            if the inputs do contain infinities or NaNs. Default: True.

    Returns:
        Tensor, inverse of the matrix `a`.

    Raises:
        LinAlgError: If :math:`a` is singular.
        ValueError: If :math:`a` is not square, or not 2D.

    Supported Platforms:
        ``CPU`` ``GPU``

    Examples:
        >>> import numpy as onp
        >>> from mindspore.common import Tensor
        >>> import mindspore.numpy as mnp
        >>> from mindspore.scipy.linalg import inv
        >>> a = Tensor(onp.array([[1., 2.], [3., 4.]]))
        >>> inv(a)
        Tensor(shape=[2, 2], dtype=Float64, value=
        [[-2.00000000e+00,  1.00000000e+00],
         [ 1.50000000e+00, -5.00000000e-01]])
        >>> mnp.dot(a, inv(a))
        Tensor(shape=[2, 2], dtype=Float64, value=
        [[ 1.00000000e+00,  0.00000000e+00],
         [ 8.88178420e-16,  1.00000000e+00]])
    """
    if F.dtype(a) not in float_types:
        a = F.cast(a, mstype.float32)

    matrix_inverse = P.MatrixInverse(adjoint=False)
    return matrix_inverse(a)


def cho_factor(a, lower=False, overwrite_a=False, check_finite=True):
    """
    Compute the Cholesky decomposition of a matrix, to use in cho_solve

    Returns a matrix containing the Cholesky decomposition,
    ``A = L L*`` or ``A = U* U`` of a Hermitian positive-definite matrix `a`.
    The return value can be directly used as the first parameter to cho_solve.

    .. warning::
        The returned matrix also contains random data in the entries not
        used by the Cholesky decomposition. If you need to zero these
        entries, use the function `cholesky` instead.

    Args:
        a (Tensor): square Matrix of (M, M) to be decomposed
        lower (bool, optional): Whether to compute the upper or lower triangular Cholesky factorization
            (Default: upper-triangular)
        overwrite_a(bool, optional): Whether to overwrite data in a (may improve performance)
        check_finite(bool, optional): Whether to check that the input matrix contains only finite numbers.
            Disabling may give a performance gain, but may result in problems
            (crashes, non-termination) if the inputs do contain infinities or NaNs.

    Returns:
         - Tensor, matrix whose upper or lower triangle contains the Cholesky factor of `a`.
        Other parts of the matrix contain random data.
         - bool, flag indicating whether the factor is in the lower or upper triangle

    Raises:
        LinAlgError: Raised if decomposition fails.

    Supported Platforms:
        ``CPU`` ``GPU``

    Examples:
        >>> import numpy as onp
        >>> from mindspore.common import Tensor
        >>> from mindspore.scipy.linalg import cho_factor
        >>> A = Tensor(onp.array([[9, 3, 1, 5], [3, 7, 5, 1], [1, 5, 9, 2], [5, 1, 2, 6]]).astype(onp.float32))
        >>> c, low = cho_factor(A)
        >>> c
        Tensor(shape=[4, 4], dtype=Float32, value=
        [[ 3.00000000e+00,  1.00000000e+00,  3.33333343e-01,  1.66666663e+00],
         [ 3.00000000e+00,  2.44948983e+00,  1.90515852e+00, -2.72165507e-01],
         [ 1.00000000e+00,  5.00000000e+00,  2.29330778e+00,  8.55952621e-01],
         [ 5.00000000e+00,  1.00000000e+00,  2.00000000e+00,  1.55418575e+00]])
    """
    cholesky_net = Cholesky(lower=lower, clean=False)
    c = cholesky_net(a)
    return c, lower


def cholesky(a, lower=False, overwrite_a=False, check_finite=True):
    """
    Compute the Cholesky decomposition of a matrix.

    Returns the Cholesky decomposition, :math:`A = L L^*` or
    :math:`A = U^* U` of a Hermitian positive-definite matrix A.

    Args:
        a (Tensor): square Matrix of (M, M) to be decomposed
        lower (bool, optional): Whether to compute the upper- or lower-triangular Cholesky
            factorization.  Default is upper-triangular.
        overwrite_a (bool, optional): Whether to overwrite data in `a` (may improve performance).
        check_finite (bool, optional): Whether to check that the input matrix contains only finite numbers.
            Disabling may give a performance gain, but may result in problems
            (crashes, non-termination) if the inputs do contain infinities or NaNs.

    Returns:
        Tensor, upper- or lower-triangular Cholesky factor of `a`.

    Raises:
        LinAlgError: if decomposition fails.

    Supported Platforms:
        ``CPU`` ``GPU``

    Examples:
        >>> import numpy as onp
        >>> from mindspore.common import Tensor
        >>> from mindspore.scipy.linalg import cholesky
        >>> a = Tensor(onp.array([[1, -2],[2, 5]]).astype(onp.float32))
        >>> L = cholesky(a, lower=True)
        >>> L
        Tensor(shape=[2, 2], dtype=Float32, value=
        [[ 1.00000000e+00,  0.00000000e+00],
         [ 2.00000000e+00,  1.00000000e+00]])
    """
    cholesky_net = Cholesky(lower=lower, clean=True)
    c = cholesky_net(a)
    return c


def cho_solve(c_and_lower, b, overwrite_b=False, check_finite=True):
    """Solve the linear equations Ax = b, given the Cholesky factorization of A.

    Args:
        c_and_lower ((Tensor, bool)): Cholesky factorization of a, as given by cho_factor
        b (Tensor): Right-hand side
        overwrite_b (bool, optional): Whether to overwrite data in b (may improve performance)
        check_finite (bool, optional): Whether to check that the input matrices contain only finite numbers.
            Disabling may give a performance gain, but may result in problems
            (crashes, non-termination) if the inputs do contain infinities or NaNs.

    Returns:
        Tensor, the solution to the system A x = b

    Supported Platforms:
        ``CPU`` ``GPU``

    Examples:
        >>> import numpy as onp
        >>> from mindspore.common import Tensor
        >>> from mindspore.scipy.linalg import cho_factor, cho_solve
        >>> A = Tensor(onp.array([[9, 3, 1, 5], [3, 7, 5, 1], [1, 5, 9, 2], [5, 1, 2, 6]]).astype(onp.float32))
        >>> b = Tensor(onp.array([1, 1, 1, 1]).astype(onp.float32))
        >>> c, low = cho_factor(A)
        >>> x = cho_solve((c, low), b)
        >>> x
        Tensor(shape=[4], dtype=Float32, value= [-1.74926575e-02,  1.19533479e-01,  1.16618462e-02,  1.57434344e-01])
    """
    (c, lower) = c_and_lower
    cholesky_solver_net = CholeskySolver(lower=lower)
    x = cholesky_solver_net(c, b)
    return x


def eigh(a, b=None, lower=True, eigvals_only=False, overwrite_a=False,
         overwrite_b=False, turbo=True, eigvals=None, _type=1,
         check_finite=True):
    """
    Solve a standard or generalized eigenvalue problem for a complex Hermitian or real symmetric matrix.

    Find eigenvalues Tensor `w` and optionally eigenvectors Tensor `v` of Tensor `a`,
    where `b` is positive definite such that for every eigenvalue `λ` (i-th entry of w) and
    its eigenvector `vi` (i-th column of `v`) satisfies::

                      a @ vi = λ * b @ vi
        vi.conj().T @ a @ vi = λ
        vi.conj().T @ b @ vi = 1

    In the standard problem, `b` is assumed to be the identity matrix.

    Args:
        a (Tensor): A :math:`(M, M)` complex Hermitian or real symmetric matrix whose eigenvalues and
            eigenvectors will be computed.
        b (Tensor, optional): A :math:`(M, M)` complex Hermitian or real symmetric definite positive matrix in.
            If omitted, identity matrix is assumed. Default: None.
        lower (bool, optional): Whether the pertinent Tensor data is taken from the lower or upper
            triangle of `a` and, if applicable, `b`. Default: True.
        eigvals_only (bool, optional): Whether to calculate only eigenvalues and no eigenvectors.
            Default: False.
        _type (int, optional): For the generalized problems, this keyword specifies the problem type
            to be solved for `w` and `v` (only takes 1, 2, 3 as possible inputs)::

                1 =>     a @ v = w @ b @ v
                2 => a @ b @ v = w @ v
                3 => b @ a @ v = w @ v

            This keyword is ignored for standard problems. Default: 1.
        overwrite_a (bool, optional): Whether to overwrite data in `a` (may improve performance). Default: False.
        overwrite_b (bool, optional): Whether to overwrite data in `b` (may improve performance). Default: False.
        check_finite (bool, optional): Whether to check that the input matrices contain only finite numbers.
            Disabling may give a performance gain, but may result in problems (crashes, non-termination)
            if the inputs do contain infinities or NaNs. Default: True.
        turbo (bool, optional): use divide and conquer algorithm (faster but expensive in memory, only
            for generalized eigenvalue problem and if full set of eigenvalues are requested.).
            Has no significant effect if eigenvectors are not requested. Default: True.
        eigvals (tuple, optional): Indexes of the smallest and largest (in ascending order) eigenvalues
            and corresponding eigenvectors to be returned: :math:`0 <= lo <= hi <= M-1`. If omitted, all eigenvalues
            and eigenvectors are returned. Default: None.

    Returns:
        - Tensor with shape :math:`(N,)`, the :math:`N (1<=N<=M)` selected eigenvalues, in ascending order,
          each repeated according to its multiplicity.

        - Tensor with shape :math:`(M, N)`, (if ``eigvals_only == False``)

    Raises:
        LinAlgError: If eigenvalue computation does not converge, an error occurred, or b matrix is not
            definite positive. Note that if input matrices are not symmetric or Hermitian, no error will
            be reported but results will be wrong.

    Supported Platforms:
        ``CPU`` ``GPU``

    Examples:
        >>> import mindspore.numpy as mnp
        >>> from mindspore.common import Tensor
        >>> from mindspore.scipy.linalg import eigh
        >>> A = Tensor([[6., 3., 1., 5.], [3., 0., 5., 1.], [1., 5., 6., 2.], [5., 1., 2., 2.]])
        >>> w, v = eigh(A)
        >>> mnp.sum(mnp.dot(A, v) - mnp.dot(v, mnp.diag(w))) < 1e-10
        Tensor(shape=[], dtype=Bool, value= True)
    """
    eigh_net = EighNet(not eigvals_only, lower=True)
    return eigh_net(a)


def lu_pivots_to_permutation(pivots, permutation_size: int):
    """transfer pivots to permutation"""
    batch_dims = pivots.shape[:-1]
    k = pivots.shape[-1]
    per = mnp.arange(0, permutation_size)
    permutation = mnp.broadcast_to(per, batch_dims + (permutation_size,))
    permutation = mnp.array(permutation)
    if permutation_size == 0:
        return permutation

    for i in range(k):
        j = pivots[..., i]
        loc = mnp.ix_(*(mnp.arange(0, b) for b in batch_dims))
        x = permutation[..., i]
        y = permutation[loc + (j,)]
        permutation[..., i] = y
        permutation[loc + (j,)] = x
    return permutation


def lu_solve_core(in_lu, permutation, b, trans):
    """ core implementation of lu solve"""
    m = in_lu.shape[0]
    res_shape = b.shape[1:]
    prod_result = 1
    for sh in res_shape:
        prod_result *= sh
    x = mnp.reshape(b, (m, prod_result))
    trans_str = None
    if trans == 0:
        trans_str = "N"
        x = x[permutation, :]
    elif trans == 1:
        trans_str = "T"
    elif trans == 2:
        trans_str = "C"
    else:
        _raise_value_error("trans error, it's value must be 0, 1, 2")
    ms_lu_solve = LUSolver(trans_str)
    output = ms_lu_solve(in_lu, x)
    return mnp.reshape(output, b.shape)


def check_lu_shape(in_lu, b):
    """ check lu input shape"""
    if len(in_lu.shape) < 2 or in_lu.shape[-1] != in_lu.shape[-2]:
        _raise_value_error("last two dimensions of LU decomposition must be equal.")

    if b.shape is None:
        _raise_value_error(" LU decomposition input b's rank must >=1.")

    rhs_vector = in_lu.ndim == b.ndim + 1
    if rhs_vector:
        if b.shape[-1] != in_lu.shape[-1]:
            _raise_value_error("LU decomposition: lu matrix and b must have same number of dimensions")
        mnp.expand_dims(b, axis=1)
    else:
        if b.shape[-2] != in_lu.shape[-1]:
            _raise_value_error("LU decomposition: lu matrix and b must have same number of dimensions")

    return True


def lu_factor(a, overwrite_a=False, check_finite=True):
    """
    Compute pivoted LU decomposition of a square matrix,
    and its outputs can be directly used as the inputs of `lu_solve`.
    The decomposition is:

    .. math::
        A = P L U

    where :math:`P` is a permutation matrix, :math:`L` lower triangular with unit diagonal elements,
    and :math:`U` upper triangular.

    Args:
        a (Tensor): square matrix of :math:`(M, M)` to decompose.
        overwrite_a (bool, optional): Whether to overwrite data in :math:`A` (may increase performance). Default: False.
        check_finite (bool, optional): Whether to check that the input matrix contains only finite numbers.
            Disabling may give a performance gain, but may result in problems
            (crashes, non-termination) if the inputs do contain infinities or NaNs. Default: True.

    Returns:
        - Tensor, a square matrix of :math:`(N, N)` containing `U` in its upper triangle, and `L` in its lower triangle.
          The unit diagonal elements of `L` are not stored.

        - Tensor, :math:`(N,)` pivot indices representing the permutation matrix `P`:
          the i-th element value j in the indices indicates that row i of matrix was interchanged with row j.

    Raises:
        ValueError: If :math:`a` is not square.

    Supported Platforms:
        ``CPU`` ``GPU``

    Examples:
        >>> import numpy as onp
        >>> from mindspore.common import Tensor
        >>> from mindspore.scipy.linalg import lu_factor
        >>> A = Tensor(onp.array([[2, 5, 8, 7], [5, 2, 2, 8], [7, 5, 6, 6], [5, 4, 4, 8]]).astype(onp.float64))
        >>> lu, piv = lu_factor(A)
        >>> lu
        Tensor(shape=[4, 4], dtype=Float64, value=
        [[ 7.00000000e+00,  5.00000000e+00,  6.00000000e+00,  6.00000000e+00],
         [ 2.85714286e-01,  3.57142857e+00,  6.28571429e+00,  5.28571429e+00],
         [ 7.14285714e-01,  1.20000000e-01, -1.04000000e+00,  3.08000000e+00],
         [ 7.14285714e-01, -4.40000000e-01, -4.61538462e-01,  7.46153846e+00]])
        >>> piv
        Tensor(shape=[4], dtype=Int32, value= [2, 0, 3, 1])
    """
    if len(a.shape) < 2 or (a.shape[-1] != a.shape[-2]):
        _raise_value_error("input of lu matrix must be square.")
    msp_lu = LU()
    m_lu, pivots, _ = msp_lu(a)
    return m_lu, pivots


def lu(a, permute_l=False, overwrite_a=False, check_finite=True):
    """
    Compute pivoted LU decomposition of a general matrix.

    The decomposition is:

    .. math::
        A = P L U

    where :math:`P` is a permutation matrix, :math:`L` lower triangular with unit
    diagonal elements, and :math:`U` upper triangular.

    Args:
        a (Tensor): a :math:`(M, N)` matrix to decompose.
        permute_l (bool, optional): Perform the multiplication :math:`P L` (Default: do not permute). Default: False.
        overwrite_a (bool, optional): Whether to overwrite data in :math:`A` (may improve performance). Default: False.
        check_finite (bool, optional):  Whether to check that the input matrix contains
            only finite numbers. Disabling may give a performance gain, but may result
            in problems (crashes, non-termination) if the inputs do contain infinities or NaNs. Default: True.

    Returns:
        **If permute_l == False**

        - Tensor, :math:`(M, M)` permutation matrix.
        - Tensor, :math:`(M, K)` lower triangular or trapezoidal matrix with unit diagonal. :math:`K = min(M, N)`.
        - Tensor, :math:`(K, N)` upper triangular or trapezoidal matrix.

        **If permute_l == True**

        - Tensor, :math:`(M, K)` permuted L matrix. :math:`K = min(M, N)`.
        - Tensor, :math:`(K, N)` upper triangular or trapezoidal matrix.

    Supported Platforms:
        ``CPU`` ``GPU``

    Examples:
        >>> import numpy as onp
        >>> from mindspore.common import Tensor
        >>> from mindspore.scipy.linalg import lu
        >>> A = Tensor(onp.array([[2, 5, 8, 7], [5, 2, 2, 8], [7, 5, 6, 6], [5, 4, 4, 8]]).astype(onp.float64))
        >>> p, l, u = lu(A)
        >>> p
        Tensor(shape=[4, 4], dtype=Int32, value=
        [[0, 1, 0, 0],
         [0, 0, 0, 1],
         [1, 0, 0, 0],
         [0, 0, 1, 0]])
        >>> l
        Tensor(shape=[4, 4], dtype=Float64, value=
        [[ 1.00000000e+00,  0.00000000e+00,  0.00000000e+00,  0.00000000e+00],
         [ 2.85714298e-01,  1.00000000e+00,  0.00000000e+00,  0.00000000e+00],
         [ 7.14285731e-01,  1.19999997e-01,  1.00000000e+00,  0.00000000e+00],
         [ 7.14285731e-01, -4.39999998e-01, -4.61538464e-01,  1.00000000e+00]])
        >>> u
        Tensor(shape=[4, 4], dtype=Float64, value=
        [[ 7.00000000e+00,  5.00000000e+00,  6.00000000e+00,  6.00000000e+00],
         [ 0.00000000e+00,  3.57142854e+00,  6.28571415e+00,  5.28571415e+00],
         [ 0.00000000e+00,  0.00000000e+00, -1.03999996e+00,  3.07999992e+00],
         [ 0.00000000e+00, -0.00000000e+00, -0.00000000e+00,  7.46153831e+00]])
    """
    msp_lu = LU()
    m_lu, _, p = msp_lu(a)
    m = a.shape[-2]
    n = a.shape[-1]
    k = min(m, n)
    a_dtype = a.dtype
    l = mnp.tril(m_lu, -1)[:, :k] + mnp.eye(m, k, dtype=a_dtype)
    u = mnp.triu(m_lu)[:k, :]
    if permute_l:
        return mnp.dot(p, l), u
    return p, l, u


def lu_solve(lu_and_piv, b, trans=0, overwrite_b=False, check_finite=True):
    """Solve an equation system, a x = b, given the LU factorization of a

    Args:
        lu_and_piv (Tensor, Tensor): Factorization of the coefficient matrix a, as given by lu_factor
        b (Tensor): Right-hand side
        trans (int, optional): {0, 1, 2}
            Type of system to solve:
            =====  =========
            trans  system
            =====  =========
            0      a x   = b
            1      a^T x = b
            2      a^H x = b
            =====  =========
        overwrite_b (bool, optional): Whether to overwrite data in b (may increase performance)
        check_finite ( bool, optional): Whether to check that the input matrices contain only finite numbers.
            Disabling may give a performance gain, but may result in problems (crashes, non-termination)
            if the inputs do contain infinities or NaNs.

    Returns:
        Tesnor, solution to the system

    Supported Platforms:
        ``CPU`` ``GPU``

    Examples:
        >>> import numpy as onp
        >>> from mindspore.common import Tensor
        >>> from mindspore.scipy.linalg import lu_factor, lu_solve
        >>> A = Tensor(onp.array([[2, 5, 8, 7], [5, 2, 2, 8], [7, 5, 6, 6], [5, 4, 4, 8]]).astype(onp.float64))
        >>> b = Tensor(onp.array([1, 1, 1, 1]).astype(onp.float64))
        >>> lu, piv = lu_factor(A)
        >>> lu_solve((lu, piv), b)
        [ 0.05154639, -0.08247423,  0.08247423,  0.09278351]
    """
    m_lu, pivots = lu_and_piv
    # 1. check shape
    check_lu_shape(m_lu, b)
    # here permutation array has been calculated, just use it.
    # 2. calculate permutation
    permutation = lu_pivots_to_permutation(pivots, len(pivots))
    # 3. rhs_vector
    rhs_vector = m_lu.ndim == b.ndim + 1
    x = lu_solve_core(m_lu, permutation, b, trans)
    return x[..., 0] if rhs_vector else x
