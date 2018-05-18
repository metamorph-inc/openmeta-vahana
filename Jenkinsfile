pipeline {
  agent any
  stages {
    stage('OpenMETA runner') {
      steps {
        openMetaTestBench(modelName: 'openmeta-vahana.xme')
      }
    }
  }
}