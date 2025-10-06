package com.inventory;

import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Reader;
import java.io.Writer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder; 

public class DataStore {
    private static final String FILE_PATH = "src/main/resources/data/inventory.json";
    private static Gson gson = new GsonBuilder().setPrettyPrinting().create();

    public static List<InventoryItem> loadItems() {
        try (Reader reader = new FileReader(FILE_PATH)) {
            InventoryItem[] items = gson.fromJson(reader, InventoryItem[].class);
            return items == null ? new ArrayList<>() : new ArrayList<>(Arrays.asList(items));
        } catch (IOException e) {
            return new ArrayList<>();
        }
    }

    
    public static void saveItems(List<InventoryItem> items) {
        try (Writer writer = new FileWriter(FILE_PATH)) {
            gson.toJson(items, writer);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
