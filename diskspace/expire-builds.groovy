// Force build expiration for all Jenkins jobs
// We need this script because by default expires
// jobs only when thay are actually built.

// Run by going to https://android-build.linaro.org/jenkins/script
// Or using:
// java -jar jenkins-cli.jar -s http://localhost:8080/jenkins/ -i <Jenkins API SSK key> groovy expire.groovy
// This script is expected to run via cron

for (job in hudson.model.Hudson.instance.items) {
  // That's how you print debug info:
  // println(job);

  // Be extra cautious about release builds
  if (job.name ==~ ".+(201.+|-release)")
    continue;

  job.logRotate();
}
