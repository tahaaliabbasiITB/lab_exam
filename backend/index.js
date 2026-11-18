
const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
require('dotenv').config();

const app = express();

// ---------------- MIDDLEWARE ----------------

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;


// ---------------- NEON DATABASE CONNECTION ----------------

const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: {
        rejectUnauthorized: false
    }
});


// ---------------- HOME ROUTE ----------------

app.get('/', (req, res) => {
    res.json({
        message: "Warehouse Management System API is Running!"
    });
});


// ---------------- GET ALL ITEMS ----------------

app.get('/items', async (req, res) => {

    try {

        const result = await pool.query(
            'SELECT * FROM items ORDER BY id ASC'
        );

        res.json(result.rows);

    } catch (err) {

        console.error("GET ITEMS ERROR:", err);

        res.status(500).json({
            error: err.message
        });
    }
});


// ---------------- GET SINGLE ITEM ----------------

app.get('/items/:id', async (req, res) => {

    try {

        const id = Number(req.params.id);

        if (!Number.isInteger(id) || id <= 0) {
            return res.status(400).json({
                error: "Invalid item ID"
            });
        }

        const result = await pool.query(
            'SELECT * FROM items WHERE id = $1',
            [id]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({
                error: "Item not found"
            });
        }

        res.json(result.rows[0]);

    } catch (err) {

        console.error("GET SINGLE ITEM ERROR:", err);

        res.status(500).json({
            error: err.message
        });
    }
});


// ---------------- ADD ITEM ----------------

app.post('/items', async (req, res) => {

    try {

        const { name, location } = req.body || {};

        if (
            typeof name !== 'string' || !name.trim() ||
            typeof location !== 'string' || !location.trim()
        ) {
            return res.status(400).json({
                error: "Name and location are required"
            });
        }

        const result = await pool.query(
            `INSERT INTO items (name, location)
             VALUES ($1, $2)
             RETURNING *`,
            [name.trim(), location.trim()]
        );

        res.status(201).json({
            message: "Item added successfully",
            item: result.rows[0]
        });

    } catch (err) {

        console.error("ADD ITEM ERROR:", err);

        res.status(500).json({
            error: err.message
        });
    }
});


// ---------------- UPDATE ITEM ----------------

app.put('/items/:id', async (req, res) => {

    try {

        const id = Number(req.params.id);

        const { name, location } = req.body || {};

        if (!Number.isInteger(id) || id <= 0) {
            return res.status(400).json({
                error: "Invalid item ID"
            });
        }

        if (
            typeof name !== 'string' || !name.trim() ||
            typeof location !== 'string' || !location.trim()
        ) {
            return res.status(400).json({
                error: "Name and location are required"
            });
        }

        const result = await pool.query(
            `UPDATE items
             SET name = $1, location = $2
             WHERE id = $3
             RETURNING *`,
            [name.trim(), location.trim(), id]
        );

        if (result.rows.length === 0) {
            return res.status(404).json({
                error: "Item not found"
            });
        }

        res.json({
            message: "Item updated successfully",
            item: result.rows[0]
        });

    } catch (err) {

        console.error("UPDATE ITEM ERROR:", err);

        res.status(500).json({
            error: err.message
        });
    }
});


// ---------------- DELETE ITEM ----------------

app.delete('/items/:id', async (req, res) => {

    const client = await pool.connect();

    try {

        const id = Number(req.params.id);

        if (!Number.isInteger(id) || id <= 0) {
            return res.status(400).json({
                error: "Invalid item ID"
            });
        }

        await client.query('BEGIN');

        // Delete selected item
        const result = await client.query(
            'DELETE FROM items WHERE id = $1 RETURNING *',
            [id]
        );

        if (result.rowCount === 0) {

            await client.query('ROLLBACK');

            return res.status(404).json({
                error: "Item not found"
            });
        }

        // Synchronize PostgreSQL ID sequence
        // with the highest remaining item ID

        await client.query(`
            SELECT setval(
                pg_get_serial_sequence('items', 'id'),
                COALESCE(
                    (SELECT MAX(id) FROM items),
                    0
                ) + 1,
                false
            )
        `);

        await client.query('COMMIT');

        res.json({
            message: "Item deleted successfully",
            item: result.rows[0]
        });

    } catch (err) {

        await client.query('ROLLBACK');

        console.error("DELETE ITEM ERROR:", err);

        res.status(500).json({
            error: err.message
        });

    } finally {

        client.release();
    }
});


// ---------------- SERVER START ----------------

app.listen(PORT, () => {

    console.log(
        `Warehouse Management Server running on port ${PORT}`
    );

});
