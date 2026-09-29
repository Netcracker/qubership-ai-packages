package m;

import static org.mockito.Mockito.lenient;

import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
@TestMethodOrder(MethodOrderer.MethodName.class)
class LenientTest {
    @Mock Sender sender;
    @Mock Templates templates;

    @Test
    void a_unusedLenientStub() {
        lenient().when(templates.greeting("en")).thenReturn("hello");
    }

    @Test
    void b_lenientStubCalledWithOtherArguments() {
        lenient().when(templates.greeting("en")).thenReturn("hello");
        new Notifier(sender, templates).notifyIn("fr", "bob");
    }
}
