from app.db.repositories.server_repository import ServerRepository
from app.db.repositories.network_log_repository import NetworkLogRepository


def create_test_server(db_session):
    repo = ServerRepository(db_session)

    return repo.create(
        ip_address="192.168.20.1",
        region="AP-South",
        status="Active",
    )


def test_create_network_log(db_session):
    server = create_test_server(db_session)

    repo = NetworkLogRepository(db_session)

    log = repo.create(
        node_id=server.node_id,
        error_code="ERR-500",
        latency=450.5,
    )

    assert log.log_id is not None
    assert log.node_id == server.node_id
    assert log.error_code == "ERR-500"
    assert log.latency == 450.5


def test_get_network_log(db_session):
    server = create_test_server(db_session)

    repo = NetworkLogRepository(db_session)

    created = repo.create(
        node_id=server.node_id,
        error_code=None,
        latency=25.0,
    )

    log = repo.get_by_id(created.log_id)

    assert log is not None
    assert log.log_id == created.log_id


def test_get_logs_by_node(db_session):
    server = create_test_server(db_session)

    repo = NetworkLogRepository(db_session)

    repo.create(server.node_id, None, 20.0)
    repo.create(server.node_id, "ERR-500", 500.0)
    repo.create(server.node_id, None, 30.0)

    logs = repo.get_by_node(server.node_id)

    assert len(logs) == 3


def test_update_network_log(db_session):
    server = create_test_server(db_session)

    repo = NetworkLogRepository(db_session)

    log = repo.create(
        server.node_id,
        None,
        50.0,
    )

    updated = repo.update(
        log.log_id,
        error_code="ERR-404",
        latency=404.0,
    )

    assert updated is not None
    assert updated.error_code == "ERR-404"
    assert updated.latency == 404.0


def test_delete_network_log(db_session):
    server = create_test_server(db_session)

    repo = NetworkLogRepository(db_session)

    log = repo.create(
        server.node_id,
        None,
        50.0,
    )

    deleted = repo.delete(log.log_id)

    assert deleted is not None
    assert repo.get_by_id(log.log_id) is None