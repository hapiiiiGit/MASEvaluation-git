import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Users() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // For creating a new user
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    password: '',
    role_id: '',
    is_active: true,
  });
  const [creatingUser, setCreatingUser] = useState(false);
  const [createUserError, setCreateUserError] = useState(null);

  // For creating a new role
  const [newRole, setNewRole] = useState({
    name: '',
    permissions: '',
  });
  const [creatingRole, setCreatingRole] = useState(false);
  const [createRoleError, setCreateRoleError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [usersRes, rolesRes] = await Promise.all([
          axios.get('/api/users/'),
          axios.get('/api/users/roles/'),
        ]);
        setUsers(usersRes.data);
        setRoles(rolesRes.data);
      } catch (err) {
        setError('Failed to load users or roles.');
      }
      setLoading(false);
    };
    fetchData();
  }, []);

  // Handle new user form changes
  const handleUserChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewUser({
      ...newUser,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setCreatingUser(true);
    setCreateUserError(null);

    try {
      await axios.post('/api/users/', {
        username: newUser.username,
        email: newUser.email,
        password: newUser.password,
        role_id: newUser.role_id ? parseInt(newUser.role_id, 10) : null,
        is_active: newUser.is_active,
      });
      // Refresh users
      const usersRes = await axios.get('/api/users/');
      setUsers(usersRes.data);
      setNewUser({
        username: '',
        email: '',
        password: '',
        role_id: '',
        is_active: true,
      });
    } catch (err) {
      setCreateUserError('Failed to create user.');
    }
    setCreatingUser(false);
  };

  // Handle new role form changes
  const handleRoleChange = (e) => {
    setNewRole({ ...newRole, [e.target.name]: e.target.value });
  };

  const handleCreateRole = async (e) => {
    e.preventDefault();
    setCreatingRole(true);
    setCreateRoleError(null);

    try {
      // Permissions should be a comma-separated string, convert to array
      const permissionsArray = newRole.permissions
        ? newRole.permissions.split(',').map(p => p.trim()).filter(p => p)
        : [];
      await axios.post('/api/users/roles/', {
        name: newRole.name,
        permissions: permissionsArray,
      });
      // Refresh roles
      const rolesRes = await axios.get('/api/users/roles/');
      setRoles(rolesRes.data);
      setNewRole({
        name: '',
        permissions: '',
      });
    } catch (err) {
      setCreateRoleError('Failed to create role.');
    }
    setCreatingRole(false);
  };

  return (
    <div>
      <h2 className="mb-4">User Management</h2>
      {loading ? (
        <div className="text-center my-5">
          <div className="spinner-border text-primary" role="status" />
          <div>Loading users and roles...</div>
        </div>
      ) : error ? (
        <div className="alert alert-danger">{error}</div>
      ) : (
        <>
          {/* Create User Form */}
          <div className="mb-5">
            <h4>Create User</h4>
            <form onSubmit={handleCreateUser}>
              <div className="row mb-3">
                <div className="col-md-3">
                  <label className="form-label">Username</label>
                  <input
                    type="text"
                    className="form-control"
                    name="username"
                    value={newUser.username}
                    onChange={handleUserChange}
                    required
                  />
                </div>
                <div className="col-md-3">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-control"
                    name="email"
                    value={newUser.email}
                    onChange={handleUserChange}
                    required
                  />
                </div>
                <div className="col-md-3">
                  <label className="form-label">Password</label>
                  <input
                    type="password"
                    className="form-control"
                    name="password"
                    value={newUser.password}
                    onChange={handleUserChange}
                    required
                  />
                </div>
                <div className="col-md-2">
                  <label className="form-label">Role</label>
                  <select
                    className="form-select"
                    name="role_id"
                    value={newUser.role_id}
                    onChange={handleUserChange}
                    required
                  >
                    <option value="">Select Role</option>
                    {roles.map(role => (
                      <option key={role.id} value={role.id}>
                        {role.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="col-md-1 d-flex align-items-center">
                  <div className="form-check mt-4">
                    <input
                      className="form-check-input"
                      type="checkbox"
                      name="is_active"
                      checked={newUser.is_active}
                      onChange={handleUserChange}
                      id="isActiveCheck"
                    />
                    <label className="form-check-label" htmlFor="isActiveCheck">
                      Active
                    </label>
                  </div>
                </div>
              </div>
              {createUserError && <div className="alert alert-danger mt-2">{createUserError}</div>}
              <button
                type="submit"
                className="btn btn-primary mt-3"
                disabled={creatingUser}
              >
                {creatingUser ? 'Creating...' : 'Create User'}
              </button>
            </form>
          </div>

          {/* Create Role Form */}
          <div className="mb-5">
            <h4>Create Role</h4>
            <form onSubmit={handleCreateRole}>
              <div className="row mb-3">
                <div className="col-md-4">
                  <label className="form-label">Role Name</label>
                  <input
                    type="text"
                    className="form-control"
                    name="name"
                    value={newRole.name}
                    onChange={handleRoleChange}
                    required
                  />
                </div>
                <div className="col-md-8">
                  <label className="form-label">Permissions (comma-separated)</label>
                  <input
                    type="text"
                    className="form-control"
                    name="permissions"
                    value={newRole.permissions}
                    onChange={handleRoleChange}
                    placeholder="e.g. view_users,edit_users,delete_users"
                  />
                </div>
              </div>
              {createRoleError && <div className="alert alert-danger mt-2">{createRoleError}</div>}
              <button
                type="submit"
                className="btn btn-secondary mt-3"
                disabled={creatingRole}
              >
                {creatingRole ? 'Creating...' : 'Create Role'}
              </button>
            </form>
          </div>

          {/* Users List */}
          <div className="mb-5">
            <h4>Users List</h4>
            <table className="table table-bordered table-hover">
              <thead className="table-light">
                <tr>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Active</th>
                  <th>Created At</th>
                </tr>
              </thead>
              <tbody>
                {users.map(user => (
                  <tr key={user.id}>
                    <td>{user.username}</td>
                    <td>{user.email}</td>
                    <td>{user.role ? user.role.name : '-'}</td>
                    <td>
                      {user.is_active ? (
                        <span className="badge bg-success">Yes</span>
                      ) : (
                        <span className="badge bg-danger">No</span>
                      )}
                    </td>
                    <td>
                      {user.created_at
                        ? new Date(user.created_at).toLocaleString()
                        : '-'}
                    </td>
                  </tr>
                ))}
                {users.length === 0 && (
                  <tr>
                    <td colSpan={5} className="text-center text-muted">
                      No users found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* Roles List */}
          <div>
            <h4>Roles List</h4>
            <table className="table table-bordered table-hover">
              <thead className="table-light">
                <tr>
                  <th>Name</th>
                  <th>Permissions</th>
                </tr>
              </thead>
              <tbody>
                {roles.map(role => (
                  <tr key={role.id}>
                    <td>{role.name}</td>
                    <td>
                      {role.permissions && role.permissions.length > 0
                        ? role.permissions.join(', ')
                        : '-'}
                    </td>
                  </tr>
                ))}
                {roles.length === 0 && (
                  <tr>
                    <td colSpan={2} className="text-center text-muted">
                      No roles found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

export default Users;