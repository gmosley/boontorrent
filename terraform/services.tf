# Task definition (boontorrent node)
resource "aws_ecs_task_definition" "boontorrent-node" {
  family = "boontorrent-node"
  container_definitions = "${file("task-definitions/boontorrent-node.json")}"
}

# Service definition for boontorrent node
resource "aws_ecs_service" "boontorrent-node" {
  name = "boontorrent-node"
  cluster = "${aws_ecs_cluster.boontorrent-cluster.id}"
  task_definition = "${aws_ecs_task_definition.boontorrent-node.arn}"
  iam_role = "${aws_iam_role.ecs_service_role.arn}"
  desired_count = "${var.num_nodes}"
  depends_on = ["aws_iam_role_policy.ecs_service_role_policy"]

  # load_balancer {
  #   elb_name = "${aws_elb.test-http.id}"
  #   container_name = "test-http"
  #   container_port = 8080
  # }
}

# Spot fleet for Boontorrent nodes
resource "aws_spot_fleet_request" "boon_fleet" {
  iam_fleet_role      = "arn:aws:iam::12345678:role/spot-fleet"
  spot_price          = "0.03"
  allocation_strategy = "diversified"
  target_capacity     = "${var.num_nodes}"
  valid_until         = "2020-11-04T20:44:20Z"

  launch_specification {
    instance_type     = "m4.10xlarge"
    ami               = "ami-1234"
    spot_price        = "2.793"
    placement_tenancy = "dedicated"
  }

  launch_specification {
    instance_type     = "m4.4xlarge"
    ami               = "ami-5678"
    key_name          = "my-key"
    spot_price        = "1.117"
    availability_zone = "us-west-1a"
    subnet_id         = "subnet-1234"
    weighted_capacity = 35

    root_block_device {
      volume_size = "300"
      volume_type = "gp2"
    }

    tags {
      Name = "spot-fleet-example"
    }
  }
}

# Bucket for torrent files
resource "aws_s3_bucket" "torrent_bucket" {
  bucket = "boontorrent_torrent_files"
  acl    = "private"

  tags {
    Name        = "Boontorrent Torrents Bucket"
    Environment = "Dev"
  }
}