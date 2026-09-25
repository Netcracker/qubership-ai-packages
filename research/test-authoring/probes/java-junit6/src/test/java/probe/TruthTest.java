package probe;

import static com.google.common.truth.Truth.assertThat;
import static com.google.common.truth.Truth.assertWithMessage;
import static org.junit.jupiter.api.Assertions.assertAll;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static probe.Stream.ensureBytes;
import static probe.Stream.refuse;

import java.util.List;
import org.junit.jupiter.api.Test;

/** One Truth assertion per test, each failing, in the order truth.md names them. */
class TruthTest {
    @Test
    void isEqualTo() {
        assertThat(ensureBytes(-1)).isEqualTo(0);
    }

    @Test
    void isEqualToSwapped() {
        assertThat(0).isEqualTo(ensureBytes(-1));
    }

    @Test
    void assertWithMessagePlain() {
        assertWithMessage("ensureBytes(-1)").that(ensureBytes(-1)).isEqualTo(0);
    }

    @Test
    void assertWithMessageFormat() {
        int n = -1;
        assertWithMessage("ensureBytes(%s)", n).that(ensureBytes(n)).isEqualTo(0);
    }

    @Test
    void isTrue() {
        int expected = 0;
        assertThat(expected == ensureBytes(-1)).isTrue();
    }

    @Test
    void contains() {
        assertThat(List.of(1, 2, 3)).contains(4);
    }

    @Test
    void assertAllReportsBoth() {
        assertAll(
                () -> assertWithMessage("first").that(ensureBytes(-1)).isEqualTo(0),
                () -> assertWithMessage("second").that(ensureBytes(-2)).isEqualTo(0));
    }

    @Test
    void chainStopsAtFirst() {
        assertWithMessage("first").that(ensureBytes(-1)).isEqualTo(0);
        assertWithMessage("second").that(ensureBytes(-2)).isEqualTo(0);
    }

    @Test
    void hasMessageThatContains() {
        IllegalStateException e = assertThrows(IllegalStateException.class, () -> refuse(-1));
        assertThat(e).hasMessageThat().contains("positive");
    }

    @Test
    void hasCauseThat() {
        IllegalStateException e = assertThrows(IllegalStateException.class, () -> refuse(-1));
        assertThat(e).hasCauseThat().isInstanceOf(ArithmeticException.class);
    }
}
