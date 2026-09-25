package m;

public class Notifier {
    private final Sender sender;
    private final Templates templates;

    public Notifier(Sender sender, Templates templates) {
        this.sender = sender;
        this.templates = templates;
    }

    public void notify(String name) {
        sender.send(name, "hello " + name);
    }

    public void notifyIn(String language, String name) {
        sender.send(name, templates.greeting(language) + " " + name);
    }
}
