import org.apache.spark.SparkConf
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

object SimpleApp {
  def main(args: Array[String]) {
    val logFile = "boonlog.json" // Should be some file on your system

    val conf = new SparkConf()
      .setMaster("local")
      .setAppName("Simple Application")
    val spark = SparkSession.builder.config(conf).getOrCreate()

    val logData = spark.read.json(logFile).cache()

    val count = logData.count()
    println(s"Number of records: $count")

    val locationDF = logData.filter(col("location.country").isNotNull)

    locationDF.groupBy("location.country")
      .count().sort(desc("count"))
      .show(20)

    locationDF.filter("location.country_iso = 'US'")
      .groupBy("location.city", "location.subdivision",)
      .count().sort(desc("count"))
      .show(20)

    logData.groupBy("type").count().show()

    spark.stop()
  }
}
