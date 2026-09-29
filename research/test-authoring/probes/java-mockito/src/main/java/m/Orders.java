package m;

/** Meant to commit before it notifies; the defect is the reverse order. */
public class Orders {
    private final Store store;
    private final Sender sender;

    public Orders(Store store, Sender sender) {
        this.store = store;
        this.sender = sender;
    }

    public void place(String customer, String order) {
        sender.send(customer, "placed " + order);
        store.commit(order);
    }
}
