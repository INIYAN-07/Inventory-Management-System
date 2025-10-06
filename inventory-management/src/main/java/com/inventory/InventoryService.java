package com.inventory;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

public class InventoryService {
    private List<InventoryItem> items;

    public InventoryService() {
        items = DataStore.loadItems();
    }

    public List<InventoryItem> getAll() {
        return items;
    }

    public void addItem(String name, int quantity, double price) {
        InventoryItem item = new InventoryItem(UUID.randomUUID().toString(), name, quantity, price);
        items.add(item);
        DataStore.saveItems(items);
    }

    public void deleteItem(String id) {
        items = items.stream()
                .filter(i -> !i.getId().equals(id))
                .collect(Collectors.toList());
        DataStore.saveItems(items);
    }
}
