from src.database.database import Database
import pytest


def test_inset_record_site(db_instance):
    inserted_record = db_instance.insert_record(
        table="Sites",
        columns=["name", "base_url"],
        values=["sitio1", "www.sitio1.com"],
    )
    print(inserted_record)
    assert "site_id" in inserted_record
    assert inserted_record["name"] == "sitio1"
    assert inserted_record["base_url"] == "www.sitio1.com"

def test_insert_record_ignores_underscore_columns(db_instance):
    inserted_record = db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com",]
    )

    assert "site_id" in inserted_record
    assert inserted_record["name"] == "sitio1"
    assert inserted_record["base_url"] == "www.sitio1.com"
    assert "_internal_col" not in inserted_record

def test_insert_record_invalid_table(db_instance):
    with pytest.raises(Exception):
        db_instance.insert_record(
            table="non_existent_table",
            columns=["name", "_internal_col", "base_url"],
            values=["sitio1", "secret", "www.sitio1.com",]
        )

def test_select_all_records(db_instance):
    db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com",]
    )
    db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    db_instance.insert_record(
        table="Sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )

    rows = db_instance.select_records(table="Sites")
    assert rows is not None
    assert len(rows) == 3


def test_select_specific_columns(db_instance):
    db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com", ]
    )
    db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    db_instance.insert_record(
        table="Sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )
    rows = db_instance.select_records(table="Sites", columns=["name", "site_id"])

    assert rows is not None
    assert len(rows) == 3
    assert len(rows[0]) == 2
    assert "site_id" in rows[0]
    assert "name" in rows[0]

def test_select_with_equal_where_clause(db_instance):
    r1 = db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com", ]
    )
    db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    db_instance.insert_record(
        table="Sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )
    rows = db_instance.select_records(
        table="Sites", where_columns=["site_id"], where_operators=["="], where_values=[r1["site_id"]]
    )
    assert len(rows) == 1
    assert rows[0]["site_id"] == r1["site_id"]


def test_update_records(db_instance):
    db_instance.insert_record(
        table="Sites",
        columns=["name", "base_url"],
        values=["sitio1", "www.sitio1.com", ]
    )
    r2=db_instance.insert_record(
        table="Sites",
        columns=["name", "base_url"],
        values=["sitio2", "www.sitio2.com", ]
    )
    db_instance.insert_record(
        table="Sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )

    # Update record
    r2_updated = db_instance.update_records(
        table="Sites",
        columns=["name"],
        values=["sitio2_nuevo_nombre"],
        where_columns=["site_id"],
        where_operators=["="],
        where_values=[r2["site_id"]]
    )

    assert r2_updated[0]["name"] == "sitio2_nuevo_nombre"

def test_insert_update_select_record(db_instance):
    inserted_record = db_instance.insert_record(
        table="Sites",
        columns=["name", "base_url"],
        values=["sitio_A", "www.sitio-a.com"]
    )
    updated_record = db_instance.update_records(
        table="Sites",
        columns=["base_url"],
        values=["www.newsite-a.com"],
        where_columns=["site_id"],
        where_operators=["="],
        where_values=[inserted_record["site_id"]]
    )
    assert len(updated_record) == 1

    selected_record = db_instance.select_records(
        table="Sites",
        where_columns=["site_id"],
        where_operators=["="],
        where_values=[updated_record[0]["site_id"]]
    )

    assert len(selected_record) == 1
    assert selected_record[0] == updated_record[0]


def test_delete_records(db_instance):
    r1 = db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com", ]
    )
    r2 = db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    r3 = db_instance.insert_record(
        table="Sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )

    all_records_initial = db_instance.select_records(
        table="Sites",
    )

    # Delete operations
    r_deleted = db_instance.delete_records(
        table="Sites",
        where_columns=["site_id"],
        where_operators=[">"],
        where_values=[r1["site_id"]]   # Delete 2 records inserted after r1
    )

    all_records_final = db_instance.select_records(
        table="Sites"
    )

    # Check 2 records deleted
    assert len(all_records_initial) - 2 == len(all_records_final)
    assert r_deleted[0] == r2 or r_deleted[0] == r3
    assert r_deleted[1] == r2 or r_deleted[1] == r3

def test_safe_deleted_without_where(db_instance):
    r1 = db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com", ]
    )
    r2 = db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    r3 = db_instance.insert_record(
        table="Sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )

    with pytest.raises(ValueError):
        db_instance.delete_records(table="Sites")

def test_deletes_on_nothing_satisfies_where_condition(db_instance):
    r1 = db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com", ]
    )
    r2 = db_instance.insert_record(
        table="Sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    r3 = db_instance.insert_record(
        table="Sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )

    records_deleted = db_instance.delete_records(
        table="Sites",
        where_columns=["site_id"],
        where_operators=[">"],
        where_values=[r3["site_id"]]
    )
    assert len(records_deleted) == 0