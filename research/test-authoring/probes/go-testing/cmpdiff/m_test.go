package cmpdiff

import (
	"testing"

	"github.com/google/go-cmp/cmp"
)

type Header struct {
	Name  string
	Count int
	Tags  []string
}

func parseHeader(string) Header { return Header{Name: "stream", Count: -1, Tags: []string{"a", "c"}} }

func TestParseHeader(t *testing.T) {
	want := Header{Name: "stream", Count: 0, Tags: []string{"a", "b"}}
	got := parseHeader("stream;-1;a,c")
	if diff := cmp.Diff(want, got); diff != "" {
		t.Errorf("parseHeader() mismatch (-want +got):\n%s", diff)
	}
}

// The raw return value of cmp.Diff, printed with no label around it.
func TestRawDiff(t *testing.T) {
	t.Log(cmp.Diff(0, -1))
	t.Fail()
}
