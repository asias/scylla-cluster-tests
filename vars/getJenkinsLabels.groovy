#!groovy
import groovy.json.JsonSlurper

def call(String backend, String aws_region=null) {
    try {
        regionList = new JsonSlurper().parseText(aws_region)
        aws_region = regionList[0]
    } catch(Exception) {

    }

    def jenkins_labels = ['aws-eu-west-1': 'aws-sct-builders-eu-west-1',
                          'aws-eu-west-2': 'aws-sct-builders-eu-west-2',
                          'aws-eu-north-1': 'aws-sct-builders-eu-north-1',
                          'aws-eu-central-1': 'aws-sct-builders-eu-central-1',
                          'aws-us-east-1' : 'aws-sct-builders-us-east-1',
                          'gce': 'gce-sct-builders',
                          'docker': 'sct-builders']

    if (backend == 'aws' && aws_region)
    {
        println("Finding builder for AWS region: " + aws_region)
        if (aws_region == "random"){
            def aws_supported_regions = ["eu-west-2", "eu-north-1", "eu-central-1"]
            Collections.shuffle(aws_supported_regions)
            aws_region = aws_supported_regions[0]
        }

        label = jenkins_labels.get("${backend}-${aws_region}", null)
        if (label != null){
            println("Found AWS builder with label: " + label)
            return [ "label": label, "region": aws_region ]
        }
        else{
            throw new Exception("=================== AWS region ${aws_region} not supported ! ===================")
        }

    }
    else
    {
        return [ "label": jenkins_labels[backend] ]
    }
}
