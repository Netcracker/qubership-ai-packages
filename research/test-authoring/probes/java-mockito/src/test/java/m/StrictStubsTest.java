package m;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
@TestMethodOrder(MethodOrderer.MethodName.class)
class StrictStubsTest {
    @Mock Sender sender;
    @Mock Templates templates;

    @Test
    void a_unusedStub() {
        when(templates.greeting("en")).thenReturn("hello");
        new Notifier(sender, templates).notify("bob");
        verify(sender).send("bob", "hello bob");
        System.out.println("a_unusedStub: the body ran to its end");
    }

    @Test
    void b_stubCalledWithOtherArguments() {
        when(templates.greeting("en")).thenReturn("hello");
        new Notifier(sender, templates).notifyIn("fr", "bob");
        System.out.println("b_stubCalledWithOtherArguments: the body ran to its end");
    }

    @Test
    void c_unusedStubOnMockCreatedInBody() {
        Templates local = mock(Templates.class);
        when(local.greeting("en")).thenReturn("hello");
        assertEquals(0, 0);
    }
}
