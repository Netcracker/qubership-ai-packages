package m;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;

/** No MockitoExtension: the mocks come from Mockito.mock(). */
@TestMethodOrder(MethodOrderer.MethodName.class)
class PlainMockTest {
    Sender sender = mock(Sender.class);
    Templates templates = mock(Templates.class);

    @Test
    void a_unusedStub() {
        when(templates.greeting("en")).thenReturn("hello");
    }

    @Test
    void b_stubCalledWithOtherArguments() {
        when(templates.greeting("en")).thenReturn("hello");
        new Notifier(sender, templates).notifyIn("fr", "bob");
    }
}
