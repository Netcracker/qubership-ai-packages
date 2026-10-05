// Probe module for the Go testing and testify claims in the test-authoring skill; see ../README.md.
// Renovate's gomod manager bumps the requirements and the toolchain line, and refreshes go.sum.
module probes.example/gotesting

go 1.27.0

toolchain go1.27.1

require (
	github.com/google/go-cmp v0.7.0
	github.com/stretchr/testify v1.12.1
)

require go.yaml.in/yaml/v3 v3.0.5 // indirect
