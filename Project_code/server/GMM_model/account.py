import create_account as ca

class Account:
    """
    An account for a user based on username
    """
    def __init__(self, username):
        self.username = username
        self.gmm = None

    def create_account(self):
        means, invstds, self.gmm = ca.create_account(self.username)
        return means, invstds

    def update_gmm(self):
        ca.write_features(self.username)

    def fit_gmm(self, means, invstds):
        self.gmm = ca.fit_gmm(self.username, means, invstds)
