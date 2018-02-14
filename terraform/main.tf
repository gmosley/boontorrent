# https://github.com/hashicorp/best-practices/tree/master/terraform/providers/aws
# https://github.com/alex/ecs-terraform

provider "aws" {
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  region = "${var.region}"
  version = "~> 1.9"
}

# Create iam roles and policies for terraform
resource "aws_iam_role" "ecs_host_role" {
  name = "ecs_host_role"
  assume_role_policy = "${file("policies/ecs-role.json")}"
}

resource "aws_iam_role_policy" "ecs_instance_role_policy" {
  name = "ecs_instance_role_policy"
  policy = "${file("policies/ecs-instance-role-policy.json")}"
  role = "${aws_iam_role.ecs_host_role.id}"
}

resource "aws_iam_role" "ecs_service_role" {
  name = "ecs_service_role"
  assume_role_policy = "${file("policies/ecs-role.json")}"
}

resource "aws_iam_role_policy" "ecs_service_role_policy" {
  name = "ecs_service_role_policy"
  policy = "${file("policies/ecs-service-role-policy.json")}"
  role = "${aws_iam_role.ecs_service_role.id}"
}


# Cluster definition
resource "aws_ecs_cluster" "boontorrent-cluster" {
  name = "${var.ecs_cluster_name}"
}

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
  desired_count = 2
  depends_on = ["aws_iam_role_policy.ecs_service_role_policy"]

  # load_balancer {
  #   elb_name = "${aws_elb.test-http.id}"
  #   container_name = "test-http"
  #   container_port = 8080
  # }
}