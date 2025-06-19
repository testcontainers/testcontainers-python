import json

from keycloak import KeycloakAdmin, KeycloakOpenID

from testcontainers.keycloak import KeycloakContainer


def basic_example():
    with KeycloakContainer() as keycloak:
        # Get connection parameters
        host = keycloak.get_container_host_ip()
        port = keycloak.get_exposed_port(keycloak.port)
        admin_username = keycloak.admin_username
        admin_password = keycloak.admin_password

        # Create admin client
        admin = KeycloakAdmin(
            server_url=f"http://{host}:{port}/",
            username=admin_username,
            password=admin_password,
            realm_name="master",
            verify=False,
        )
        print("Connected to Keycloak as admin")

        # Create realm
        realm_name = "test-realm"
        admin.create_realm(payload={"realm": realm_name, "enabled": True})
        print(f"\nCreated realm: {realm_name}")

        # Switch to new realm
        admin.realm_name = realm_name

        # Create client
        client_id = "test-client"
        admin.create_client(
            payload={
                "clientId": client_id,
                "publicClient": True,
                "redirectUris": ["http://localhost:8080/*"],
                "webOrigins": ["http://localhost:8080"],
            }
        )
        print(f"Created client: {client_id}")

        # Get client details
        client = admin.get_client(client_id=client_id)
        print("\nClient details:")
        print(
            json.dumps(
                {
                    "client_id": client["clientId"],
                    "public_client": client["publicClient"],
                    "redirect_uris": client["redirectUris"],
                },
                indent=2,
            )
        )

        # Create user
        username = "testuser"
        admin.create_user(
            payload={
                "username": username,
                "email": "test@example.com",
                "enabled": True,
                "credentials": [{"type": "password", "value": "password", "temporary": False}],
            }
        )
        print(f"\nCreated user: {username}")

        # Get user details
        user = admin.get_user(user_id=username)
        print("\nUser details:")
        print(json.dumps({"username": user["username"], "email": user["email"], "enabled": user["enabled"]}, indent=2))

        # Create role
        role_name = "test-role"
        admin.create_realm_role(payload={"name": role_name, "description": "Test role"})
        print(f"\nCreated role: {role_name}")

        # Assign role to user
        role = admin.get_realm_role(role_name=role_name)
        admin.assign_realm_roles(user_id=user["id"], roles=[role])
        print(f"Assigned role {role_name} to user {username}")

        # Create group
        group_name = "test-group"
        admin.create_group(payload={"name": group_name})
        print(f"\nCreated group: {group_name}")

        # Add user to group
        group = admin.get_group_by_path(path=f"/{group_name}")
        admin.group_user_add(user_id=user["id"], group_id=group["id"])
        print(f"Added user {username} to group {group_name}")

        # Create OpenID client
        openid = KeycloakOpenID(
            server_url=f"http://{host}:{port}/", client_id=client_id, realm_name=realm_name, verify=False
        )

        # Get token
        token = openid.token(username=username, password="password")
        print("\nToken details:")
        print(
            json.dumps(
                {
                    "access_token": token["access_token"][:20] + "...",
                    "refresh_token": token["refresh_token"][:20] + "...",
                    "expires_in": token["expires_in"],
                },
                indent=2,
            )
        )

        # Get user info
        userinfo = openid.userinfo(token["access_token"])
        print("\nUser info:")
        print(json.dumps(userinfo, indent=2))

        # Get realm roles
        roles = admin.get_realm_roles()
        print("\nRealm roles:")
        for role in roles:
            print(f"- {role['name']}")

        # Get user roles
        user_roles = admin.get_realm_roles_of_user(user_id=user["id"])
        print("\nUser roles:")
        for role in user_roles:
            print(f"- {role['name']}")

        # Get groups
        groups = admin.get_groups()
        print("\nGroups:")
        for group in groups:
            print(f"- {group['name']}")

        # Get group members
        group_members = admin.get_group_members(group_id=group["id"])
        print("\nGroup members:")
        for member in group_members:
            print(f"- {member['username']}")

        # Update user
        admin.update_user(user_id=user["id"], payload={"firstName": "Test", "lastName": "User"})
        print("\nUpdated user")

        # Update client
        admin.update_client(client_id=client["id"], payload={"description": "Updated test client"})
        print("Updated client")

        # Clean up
        admin.delete_user(user_id=user["id"])
        print(f"\nDeleted user: {username}")

        admin.delete_client(client_id=client["id"])
        print(f"Deleted client: {client_id}")

        admin.delete_realm_role(role_name=role_name)
        print(f"Deleted role: {role_name}")

        admin.delete_group(group_id=group["id"])
        print(f"Deleted group: {group_name}")

        admin.delete_realm(realm_name=realm_name)
        print(f"Deleted realm: {realm_name}")


if __name__ == "__main__":
    basic_example()
