import GPy

def sample_covariance(X, kern, mu=0, num_samps=1):
    """Sample a one dimensional function as if its from a Gaussian process with
    the given covariance function."""
    dimX = X.shape
    if isscalar(mu): mu = repeat(mu, dimX)  # same for all dims if scalar
    K = kern.K(X)
    # Generate samples paths from a Gaussian with mean mu and covariance K
    F = np.random.multivariate_normal(mu, K, num_samps).T
    return F


def rbf_model(ndim, lenscale, sigvar, noisevar):
    krbf = Gpy.kern.RBF(input_dim=ndim,
                        variance=sigvar,
                        lengthscale=lenscale,
                        )
    m = GPy.models.GPRegression()