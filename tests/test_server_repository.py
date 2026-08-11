from app.db.repositories.server_repository import ServerRepository


def test_create_server(db_session):
    repo = ServerRepository(db_session)

    server = repo.create(
        ip_address="192.168.10.1",
        region="AP-South",
        status="Active",
    )

    assert server.node_id is not None
    assert server.ip_address == "192.168.10.1"
    assert server.region == "AP-South"
    assert server.status == "Active"


def test_get_server_by_id(db_session):
    repo = ServerRepository(db_session)

    created = repo.create(
        ip_address="192.168.10.2",
        region="EU-Central",
        status="Active",
    )

    server = repo.get_by_id(created.node_id)

    assert server is not None
    assert server.node_id == created.node_id


def test_get_all_servers(db_session):
    repo = ServerRepository(db_session)

    repo.create(
        ip_address="192.168.10.3",
        region="US-East",
        status="Active",
    )

    repo.create(
        ip_address="192.168.10.4",
        region="US-West",
        status="Failing",
    )

    servers = repo.get_all()

    assert len(servers) == 2


def test_update_server_status(db_session):
    repo = ServerRepository(db_session)

    server = repo.create(
        ip_address="192.168.10.5",
        region="AP-South",
        status="Active",
    )

    updated = repo.update_status(
        server.node_id,
        "Failing",
    )

    assert updated is not None
    assert updated.status == "Failing"


def test_delete_server(db_session):
    repo = ServerRepository(db_session)

    server = repo.create(
        ip_address="192.168.10.6",
        region="EU-Central",
        status="Active",
    )

    deleted = repo.delete(server.node_id)

    assert deleted is not None
    assert repo.get_by_id(server.node_id) is None