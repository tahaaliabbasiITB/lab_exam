const express = require('express');
const { Pool } = require('pg');
const cors = require('cors');
require('dotenv').config();

const app = express();
app.use(cors());
const PORT = process.env.PORT || 5000;

const pool = new Pool({
    connectionString : process.env.DATABASE_URL,
    ssl:{
        rejectUnauthorized : false
    }
});

app.get('/',async(req,res)=>{
    try{
        res.json("AOA, MUBARAK HO...............!");

    }catch(err){
        console.log(err);
        res.status(500).json({error:err.message});
    }
});

app.get('/items',async(req,res)=>{
    try{
        const result = await pool.query('select * from items');
        res.json(result.rows);

    }catch(err){
        console.log(err);
        res.status(500).json({error:err.message});
    }
});

app.listen(PORT,()=>{
    console.log(`Server is Running on PORT : ${PORT}`);
})