{

	"downloads" : [

		"https://github.com/AcademySoftwareFoundation/OpenCue/archive/v0.2.31.tar.gz"

	],

	"license" : "LICENSE",

	"commands" : [

		"cd proto &&"
			" {gafferRoot}/bin/python -m grpc_tools.protoc"
			" -I=."
			" --python_out=../pycue/opencue/compiled_proto"
			" --grpc_python_out=../pycue/opencue/compiled_proto"
			" ./*.proto",

	],

}
