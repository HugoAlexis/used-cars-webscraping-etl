from src.database.database import Database
import pytest

from tests.conftest import db_instance


def test_inset_record_site(db_instance):
    inserted_record = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio1", "www.sitio1.com"],
    )

    assert "site_id" in inserted_record
    assert inserted_record["name"] == "sitio1"
    assert inserted_record["base_url"] == "www.sitio1.com"

    record_from_db = db_instance.select_unique_record(
        table="sites",
        name="sitio1",
        base_url="www.sitio1.com",
    )
    assert record_from_db is not None


def test_insert_record_in_table_with_composite_key(db_instance):
    rt1 = db_instance.insert_record(
        table="table_1",
        columns=["name_t1"],
        values=["value1_t1"]
    )
    rt2 = db_instance.insert_record(
        table="table_2",
        columns=["name_t2"],
        values=["value1_t2"]
    )

    rjoint = db_instance.insert_record(
        table="joint_table1_table2",
        columns=['t1_id', 't2_id'],
        values=[rt1["t1_id"], rt2["t2_id"]]
    )
    assert "t1_id" in rjoint
    assert "t2_id" in rjoint

def test_update_record_by_id_with_composite_key(db_instance):
    rt1 = db_instance.insert_record(
        table="table_1",
        columns=["name_t1"],
        values=["value1_t1"]
    )
    rt2 = db_instance.insert_record(
        table="table_2",
        columns=["name_t2"],
        values=["value1_t2"]
    )

    rjoint = db_instance.insert_record(
        table="joint_table1_table2",
        columns=['t1_id', 't2_id'],
        values=[rt1["t1_id"], rt2["t2_id"]]
    )

    rt3 = db_instance.insert_record(
        table="table_2",
        columns=["name_t2"],
        values=["value2_t2"]
    )

    db_instance.update_record_by_id(
        table="joint_table1_table2",
        columns=["t1_id", "t2_id"],
        new_values=[rt1["t1_id"], rt3["t2_id"]],
        id=[rt1["t1_id"], rt2["t2_id"]]
    )

    updated_rjoint = db_instance.select_record_by_id(
        table="joint_table1_table2",
        id=[rt1["t1_id"], rt3["t2_id"]]
    )
    assert updated_rjoint is not None



def test_insert_record_ignores_underscore_columns(db_instance):
    inserted_record = db_instance.insert_record(
        table="sites",
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
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com",]
    )
    db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )

    rows = db_instance.select_records(table="sites")
    assert rows is not None
    assert len(rows) == 3


def test_select_specific_columns(db_instance):
    db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com", ]
    )
    db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )
    rows = db_instance.select_records(table="sites", columns=["name", "site_id"])

    assert rows is not None
    assert len(rows) == 3
    assert len(rows[0]) == 2
    assert "site_id" in rows[0]
    assert "name" in rows[0]

def test_select_with_equal_where_clause(db_instance):
    r1 = db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com", ]
    )
    db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )
    rows = db_instance.select_records(
        table="sites", where_columns=["site_id"], where_operators=["="], where_values=[r1["site_id"]]
    )
    assert len(rows) == 1
    assert rows[0]["site_id"] == r1["site_id"]


def test_update_records(db_instance):
    db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio1", "www.sitio1.com", ]
    )
    r2=db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio2", "www.sitio2.com", ]
    )
    db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )

    # Update record
    r2_updated = db_instance.update_records(
        table="sites",
        columns=["name"],
        values=["sitio2_nuevo_nombre"],
        where_columns=["site_id"],
        where_operators=["="],
        where_values=[r2["site_id"]]
    )

    assert r2_updated[0]["name"] == "sitio2_nuevo_nombre"

def test_insert_update_select_record(db_instance):
    inserted_record = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio_A", "www.sitio-a.com"]
    )
    updated_record = db_instance.update_records(
        table="sites",
        columns=["base_url"],
        values=["www.newsite-a.com"],
        where_columns=["site_id"],
        where_operators=["="],
        where_values=[inserted_record["site_id"]]
    )
    assert len(updated_record) == 1

    selected_record = db_instance.select_records(
        table="sites",
        where_columns=["site_id"],
        where_operators=["="],
        where_values=[updated_record[0]["site_id"]]
    )

    assert len(selected_record) == 1
    assert selected_record[0] == updated_record[0]


def test_delete_records(db_instance):
    r1 = db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com", ]
    )
    r2 = db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    r3 = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )

    all_records_initial = db_instance.select_records(
        table="sites",
    )

    # Delete operations
    r_deleted = db_instance.delete_records(
        table="sites",
        where_columns=["site_id"],
        where_operators=[">"],
        where_values=[r1["site_id"]]   # Delete 2 records inserted after r1
    )

    all_records_final = db_instance.select_records(
        table="sites"
    )

    # Check 2 records deleted
    assert len(all_records_initial) - 2 == len(all_records_final)
    assert r_deleted[0] == r2 or r_deleted[0] == r3
    assert r_deleted[1] == r2 or r_deleted[1] == r3

def test_safe_deleted_without_where(db_instance):
    r1 = db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com", ]
    )
    r2 = db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    r3 = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )

    with pytest.raises(ValueError):
        db_instance.delete_records(table="sites")

def test_deletes_nothing_when_nothing_satisfies_where_condition(db_instance):
    r1 = db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com", ]
    )
    r2 = db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    r3 = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )

    records_deleted = db_instance.delete_records(
        table="sites",
        where_columns=["site_id"],
        where_operators=[">"],
        where_values=[r3["site_id"]]
    )
    assert len(records_deleted) == 0


def test_get_primary_key(db_instance):
    pkey = db_instance.get_primary_key_column(table="sites")
    assert pkey == "site_id"


def test_get_primary_key_for_composite_pk(db_instance):
    pkey = db_instance.get_primary_key_column(table="car_snapshots")
    assert len(pkey) == 2
    assert pkey[0] == 'scrape_id'
    assert pkey[1] == 'car_id'


def test_select_record_by_id(db_instance):
    r1 = db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com", ]
    )
    r2 = db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    r3 = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )

    record_selected = db_instance.select_record_by_id("sites", r2["site_id"])
    assert isinstance(record_selected, dict)
    assert record_selected["site_id"] == r2["site_id"]

#@pytest.mark.skip(reason="Not fixed")
def test_select_record_by_id_with_composite_primary_key(db_instance):
    rt1 = db_instance.insert_record(
        table="table_1",
        columns=["name_t1"],
        values=["value1_t1"]
    )
    rt2 = db_instance.insert_record(
        table="table_2",
        columns=["name_t2"],
        values=["value1_t2"]
    )

    rj = db_instance.insert_record(
        table="joint_table1_table2",
        columns=['t1_id', 't2_id'],
        values=[rt1["t1_id"], rt2["t2_id"]]
    )

    rj_from_db = db_instance.select_record_by_id(
        table="joint_table1_table2",
        id=[rt1["t1_id"], rt2["t2_id"]]
    )
    assert rj["t1_id"] == rj_from_db["t1_id"]
    assert rj["t2_id"] == rj_from_db["t2_id"]


def test_select_record_by_non_existing_id(db_instance):
    r1 = db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.sitio1.com", ]
    )
    r2 = db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio2", "secret", "www.sitio2.com", ]
    )
    r3 = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio3", "www.sitio3.com", ]
    )

    with pytest.raises(ValueError):
        record_selected = db_instance.select_record_by_id("sites", r3["site_id"] + 1)

def test_update_record_by_id_success(db_instance):
    rec = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio1", "www.s1.com"]
    )

    updated = db_instance.update_record_by_id(
        table="sites",
        id=rec["site_id"],
        columns=["name", "base_url"],
        new_values=["sitio1_updated", "www.new.com"]
    )

    assert updated["name"] == "sitio1_updated"
    assert updated["base_url"] == "www.new.com"

def test_update_record_by_id_non_existing(db_instance):
    rec = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio1", "www.s1.com"]
    )

    non_existing_id = rec["site_id"] + 100

    with pytest.raises(ValueError):
        db_instance.update_record_by_id(
            "sites",
            non_existing_id,
            columns=["name"],
            new_values=["new"]
        )

def test_update_record_by_id_ignores_internal_columns(db_instance):
    rec = db_instance.insert_record(
        table="sites",
        columns=["name", "_internal_col", "base_url"],
        values=["sitio1", "secret", "www.s1.com"]
    )

    updated = db_instance.update_record_by_id(
        table="sites",
        id=rec["site_id"],
        dict_new_values={
            "name": "nuevo",
            "_internal_col": "no_deberia_actualizarse",
            "base_url": "www.actualizado.com"
        }
    )

    assert updated["name"] == "nuevo"
    assert updated["base_url"] == "www.actualizado.com"
    assert "_internal_col" not in updated

def test_update_record_by_id_with_dict_new_values(db_instance):
    rec = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio1", "www.s1.com"]
    )

    updated = db_instance.update_record_by_id(
        "sites",
        rec["site_id"],
        dict_new_values={"base_url": "www.modified.com"}
    )

    assert updated["base_url"] == "www.modified.com"


def test_update_record_by_id_columns_and_values_mismatch(db_instance):
    rec = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio1", "www.s1.com"]
    )

    with pytest.raises(ValueError):
        db_instance.update_record_by_id(
            "sites",
            rec["site_id"],
            columns=["name", "base_url"],
            new_values=["solo_un_valor"]
        )

def test_select_unique_record_found(db_instance):
    r1 = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio1", "www.sitio1.com"]
    )
    r2 = db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio2", "www.sitio2.com"]
    )

    # Unique selection
    rec = db_instance.select_unique_record(
        "sites",
        name="sitio1",
        base_url="www.sitio1.com",
    )

    assert rec is not None
    assert rec["site_id"] == r1["site_id"]
    assert rec["name"] == "sitio1"

def test_select_unique_record_none(db_instance):
    # Insert data
    db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio1", "www.sitio1.com"]
    )

    # Select non-existing combination
    rec = db_instance.select_unique_record(
        "sites",
        name="no-existe",
        base_url="inexistente.com"
    )

    assert rec is None

def test_select_unique_record_multiple_matches(db_instance):
    # Insert duplicates
    db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio_dupe", "www.dupe.com"]
    )
    db_instance.insert_record(
        table="sites",
        columns=["name", "base_url"],
        values=["sitio_dupe", "www.dupe.com"]
    )

    # Should raise ValueError
    with pytest.raises(ValueError):
        db_instance.select_unique_record(
            "sites",
            name="sitio_dupe",
            base_url="www.dupe.com"
        )

def test_select_unique_record_no_conditions(db_instance):
    # Verify ValueError raised on no conditions
    with pytest.raises(ValueError):
        db_instance.select_unique_record("sites")