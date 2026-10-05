package m;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.verifyNoMoreInteractions;

import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InOrder;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
@TestMethodOrder(MethodOrderer.MethodName.class)
class VerifyTest {
    @Mock Sender sender;
    @Mock Templates templates;
    @Mock Backend backend;
    @Mock Store store;

    @Test
    void a_neverCalled() {
        verify(sender).send("bob", "hello bob");
    }

    @Test
    void b_differentArguments() {
        new Notifier(sender, templates).notify("bob");
        verify(sender).send("bob", "hi bob");
    }

    @Test
    void c_calledOnceWantedTwice() {
        new Notifier(sender, templates).notify("bob");
        verify(sender, times(2)).send(anyString(), anyString());
    }

    @Test
    void d_unverifiedCall() {
        new Notifier(sender, templates).notify("bob");
        verifyNoMoreInteractions(sender);
    }

    @Test
    void e_rejectedInput() {
        new Notifier(sender, templates).notify("");
        verifyNoInteractions(sender);
    }

    @Test
    void f_cacheHit() {
        Cache cache = new Cache(backend);
        cache.get("k");
        cache.get("k");
        verify(backend, times(1)).load("k");
    }

    @Test
    void g_commitBeforeNotification() {
        new Orders(store, sender).place("bob", "o-1");
        InOrder order = inOrder(store, sender);
        order.verify(store).commit("o-1");
        order.verify(sender).send("bob", "placed o-1");
    }

    @Test
    void h_captor() {
        new Notifier(sender, templates).notify("bob");
        ArgumentCaptor<String> text = ArgumentCaptor.forClass(String.class);
        verify(sender).send(anyString(), text.capture());
        assertEquals("hi bob", text.getValue());
    }
}
