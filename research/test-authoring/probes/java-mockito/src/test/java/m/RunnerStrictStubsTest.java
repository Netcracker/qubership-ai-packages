package m;

import static org.mockito.Mockito.when;

import org.junit.FixMethodOrder;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.MethodSorters;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;

@RunWith(MockitoJUnitRunner.StrictStubs.class)
@FixMethodOrder(MethodSorters.NAME_ASCENDING)
public class RunnerStrictStubsTest {
    @Mock Sender sender;
    @Mock Templates templates;

    @Test
    public void a_unusedStub() {
        when(templates.greeting("en")).thenReturn("hello");
    }

    @Test
    public void b_stubCalledWithOtherArguments() {
        when(templates.greeting("en")).thenReturn("hello");
        new Notifier(sender, templates).notifyIn("fr", "bob");
    }
}
