package com.inventory;

import com.google.gson.Gson;

import static spark.Spark.delete;
import static spark.Spark.get;
import static spark.Spark.port;
import static spark.Spark.post;
import static spark.Spark.staticFiles;

public class Main {
    public static void main(String[] args) {
        port(8080);
        InventoryService service = new InventoryService();
        Gson gson = new Gson();

        staticFiles.location("/templates");

        get("/items", (req, res) -> {
            res.type("application/json");
            return gson.toJson(service.getAll());
        });

        post("/add", (req, res) -> {
            InventoryItem item = gson.fromJson(req.body(), InventoryItem.class);
            service.addItem(item.getName(), item.getQuantity(), item.getPrice());
            res.status(201);
            return "Added";
        });

        delete("/delete/:id", (req, res) -> {
            service.deleteItem(req.params(":id"));
            res.status(204);
            return "Deleted";
        });
    }
}
