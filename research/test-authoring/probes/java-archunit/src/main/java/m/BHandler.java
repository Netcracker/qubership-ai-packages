package m;

/** The defect: a handler without its annotation. */
public class BHandler implements Handler {
    @Override
    public void handle(String message) {}
}
