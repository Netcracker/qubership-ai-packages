package m;

import static org.mockito.Mockito.when;

import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;

/** The unused stub alone, because the runner reports it only when every test in the class passed. */
@RunWith(MockitoJUnitRunner.StrictStubs.class)
public class RunnerStrictStubsUnusedTest {
    @Mock Templates templates;

    @Test
    public void unusedStub() {
        when(templates.greeting("en")).thenReturn("hello");
    }
}
