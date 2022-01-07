from TestObject import t

class CustomLibrary:
    '''This is a user written keyword library.
    These libraries can be pretty handy for more complex tasks an typically
    more efficiant to implement compare to Resource files.

    However, they are less simple in syntax and less transparent in test protocols.

    The TestObject object (t) has the following public functions:

    class TestObject:
        def authenticate(self, login: str, password: str) -> str: ...
        def logout(self, token): ...
        def get_user_id(self, token, login) -> str: ...
        def get_user_name(self, token, user_id) -> str: ...
        def get_user(self, token, user_id=None) -> Dict[str, str]: ...
        def get_user_all(self, token) -> List[Dict[str, str]]: ...
        def delete_user(self, token, userid): ...
        def get_logout(self, token): ...
        def put_user_password(self, token, new_password, user_id=None): ...
        def put_user_name(self, token, name, user_id=None): ...
        def put_user_right(self, token, right, user_id): ...
        def post_new_user(self, token, name, login) -> str: ...
    '''

    def __init__(self, tc_session_reset=True) -> None:
        '''When option for resetting the user session each test (`tc_session_reset`)
        is set to `True` a `Login User` has to be called each test.
        Otherwise, the library keeps the session for the whole robot framework suite.'''
        self.ROBOT_LIBRARY_SCOPE = 'TEST' if tc_session_reset else 'SUITE'
        self._session = None

    @property
    def session(self):
        if self._session is None:
            raise PermissionError('No valid user session. Authenticate first!')
        return self._session

    def login_user(self, login, password) -> None:
        '''`Login User` authenticates a user to the backend.

        The session will be stored during this test suite.'''
        self._session = t.authenticate(login, password)

    def logout_user(self):
        '''Logs out the current user.'''
        t.logout(self.session)

    def create_new_user(self, name, login, password, right):
        '''Creates a new user with the give data.'''
        user_id = t.post_new_user(self.session, name, login)
        t.put_user_password(self.session, password, user_id=user_id)
        t.put_user_right(self.session, right, user_id)

    def change_own_password(self, new_password, old_password):
        '''Changes the own password given the new and current one.'''
        t.put_user_password(self.session, new_password, old_password)

    def change_users_password(self, login, new_password):
        '''Changes the password of a user by its name.
        Requires Admin priviliges!'''
        user_id = self.get_user_id(login)
        t.put_user_password(self.session, new_password, user_id=user_id)

    def get_all_users(self):
        '''`Get All Users` does return a list of user-dictionaries.

        A user dictionary has the keys `name`, `login`, `right` and `active`.
        This keyword need Admin privileges.

        Example:
        `{'name': 'Peter Parker', 'login': 'spider', 'right': 'user', 'active': True}`
        '''
        return t.get_user_all(self.session)

    def get_user_details(self, user_id=None):
        '''Returs the user details of the given user_id of if None the own user data.'''
        return t.get_user(self.session, user_id)

    def get_user_id(self, login):
        '''Returns the user_id based on login.'''
        return t.get_user_id(self.session, login)