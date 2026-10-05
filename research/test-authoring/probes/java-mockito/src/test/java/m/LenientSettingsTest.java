package m;

import static org.mockito.Mockito.when;

import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.junit.jupiter.MockitoSettings;
import org.mockito.quality.Strictness;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
@TestMethodOrder(MethodOrderer.MethodName.class)
class LenientSettingsTest {
    @Mock Sender sender;
    @Mock Templates templates;

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
