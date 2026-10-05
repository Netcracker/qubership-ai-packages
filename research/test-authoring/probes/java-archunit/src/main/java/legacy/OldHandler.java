package legacy;

import m.Handler;

/** A violation that predates the rule, which the frozen rule records. */
public class OldHandler implements Handler {
    @Override
    public void handle(String message) {}
}
