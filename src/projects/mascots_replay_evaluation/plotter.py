import matplotlib.pyplot as plt

#Data to plot
set_180 = [33.9, 72.3, 10.065, 10.139000000000001, 10.033, 20.201, 20.067, 20.209, 20.078, 22.804000000000002, 20.081000000000003, 20.150000000000002, 20.17, 20.148, 20.07, 20.136000000000003, 20.105, 20.11, 20.184, 20.099, 31.098, 20.084, 20.172, 22.735, 20.150000000000002, 20.083, 20.142, 20.17, 20.152, 20.157999999999998, 20.212, 20.081000000000003, 20.204, 20.074, 20.156, 20.116, 20.154999999999998, 20.183, 20.163, 20.144, 20.135, 20.075, 20.135, 20.080000000000002, 38.824999999999996, 20.149, 20.119, 20.122, 20.182, 20.069, 20.154, 20.285, 42.467999999999996, 20.111, 21.259, 20.115000000000002, 20.112000000000002, 20.13, 20.16, 20.134, 20.115000000000002, 20.137999999999998, 20.082, 20.157, 20.074, 20.207, 20.125, 20.134, 20.156, 20.153000000000002, 20.226000000000003, 20.136999999999997, 20.112000000000002, 20.255, 20.105999999999998, 20.168, 20.112000000000002, 20.19, 20.072, 20.168, 20.067999999999998, 20.156, 20.108, 20.148, 20.067999999999998, 20.137999999999998, 20.141, 20.218, 20.127, 20.139, 20.066, 20.162, 20.082, 20.142, 20.09, 20.141, 20.082, 20.167, 20.105999999999998, 20.147000000000002, 20.064999999999998, 20.152, 20.07, 20.157999999999998, 20.13, 20.22, 20.167, 20.144, 20.069, 20.147000000000002, 20.067999999999998, 20.163, 20.060000000000002, 20.143, 20.074, 20.160999999999998, 20.063000000000002, 20.162, 20.118000000000002, 20.162, 20.077, 20.167, 41.483, 20.195999999999998, 20.078, 20.166, 20.187, 20.118000000000002, 20.080000000000002, 20.188000000000002, 20.18, 20.179, 24.742, 20.121, 20.088, 20.111, 24.1, 20.11, 20.082, 20.121, 23.48, 20.261000000000003, 20.081000000000003, 20.188000000000002, 22.58, 23.269000000000002, 20.09, 20.117, 20.108999999999998, 20.11, 20.11, 20.107, 20.108999999999998, 20.174, 20.086, 20.102999999999998, 20.076, 20.102999999999998, 20.089, 20.131, 20.089, 20.14, 20.070999999999998, 20.135, 20.073, 20.201, 20.080000000000002, 20.129, 20.076, 20.148, 20.09, 20.121, 20.059, 20.135, 22.965, 20.135, 20.079, 20.169, 20.119, 20.150000000000002, 20.060000000000002, 20.124, 20.075, 20.131, 20.081000000000003, 20.156, 20.069, 20.314, 23.972, 20.128, 20.072, 20.136000000000003, 20.09, 20.169, 20.119, 20.14, 20.07, 20.128, 20.064, 20.149, 20.064999999999998, 20.108999999999998, 20.134, 20.064999999999998, 20.141, 20.070999999999998, 20.136999999999997, 20.07, 20.203, 20.060000000000002, 20.144, 20.070999999999998, 20.159, 20.067999999999998, 20.152, 20.061, 20.156, 20.117, 20.150000000000002, 20.069, 20.151, 120.28800000000001, 594.277, 20.147000000000002, 24.122, 23.8, 23.932, 22.422, 23.05, 22.806, 22.894000000000002, 25.698999999999998, 22.575000000000003, 20.099, 20.159, 20.099, 20.136000000000003, 20.076, 20.124, 20.095, 20.150000000000002, 20.07, 20.134, 20.075, 20.136000000000003, 20.062, 20.129, 20.088, 20.174, 20.091, 20.242, 20.111, 20.139, 20.067, 20.111, 20.115000000000002, 20.160999999999998, 20.060000000000002, 20.19, 20.59, 20.145, 20.084, 20.173, 20.084, 20.139, 20.127, 20.160999999999998, 20.066, 20.17, 20.058, 20.154999999999998, 20.069, 20.168, 20.079, 20.154999999999998, 20.134, 20.154999999999998, 20.067999999999998, 20.17, 20.132, 20.153000000000002, 20.077, 20.192999999999998, 20.102999999999998, 20.157, 20.069, 20.149, 20.072, 20.159, 20.073, 20.17, 20.075, 20.160999999999998, 20.070999999999998, 20.156, 20.078, 20.149, 20.091, 20.147000000000002, 20.125, 20.207, 20.096, 20.153000000000002, 20.080000000000002, 20.152, 20.077, 20.195999999999998, 20.111, 20.166, 20.114, 20.146, 20.099, 20.139, 20.080000000000002, 20.146, 20.11, 20.145, 20.108999999999998, 20.142, 20.091, 20.151, 20.145, 20.204, 20.124, 20.159, 20.087, 20.14, 20.088, 20.137999999999998, 20.092, 20.128, 20.115000000000002, 20.14, 20.099, 20.125, 20.094, 20.119, 20.096, 20.115000000000002, 20.095, 20.139, 20.107, 20.178, 20.097, 20.108999999999998, 20.092, 20.1, 20.141, 20.105999999999998, 20.096, 20.139, 20.102999999999998, 20.119, 20.102999999999998, 20.083, 20.150000000000002, 20.097, 20.096, 20.111, 20.1, 20.136999999999997, 20.101999999999997]
set_160 = [13.878, 53.578, 10.063, 10.087, 10.248, 20.094, 20.147000000000002, 20.074, 20.13, 24.518, 20.133000000000003, 20.080000000000002, 20.154, 20.116, 20.205000000000002, 20.079, 20.126, 24.005, 20.127, 20.075, 20.186, 23.33, 20.134, 20.079, 20.126, 22.729, 20.133000000000003, 20.091, 20.156, 22.104, 20.141, 20.088, 20.233999999999998, 21.27, 20.117, 20.076, 20.179, 20.429, 20.14, 20.233, 20.169, 20.113, 20.133000000000003, 20.091, 20.075, 20.079, 20.080000000000002, 20.077, 20.081000000000003, 20.1, 20.092, 20.091, 20.101, 20.219, 20.078, 20.114, 20.146, 20.091, 20.09, 20.135, 20.088, 20.080000000000002, 20.084999999999997, 20.078, 20.119999999999997, 20.521, 20.082, 20.09, 20.072, 20.073, 20.083, 20.079, 20.080000000000002, 20.080000000000002, 20.087, 20.073, 20.081000000000003, 20.081000000000003, 20.07, 20.133000000000003, 20.079, 20.072, 20.077, 20.132, 20.069, 20.072, 20.091, 20.076, 20.079, 20.807, 20.091, 20.084, 20.082, 20.079, 20.091, 20.132, 20.080000000000002, 20.137999999999998, 20.088, 20.086, 20.1, 20.087, 20.099, 20.074, 20.09, 20.1, 20.087, 20.097, 20.074, 20.076, 20.081000000000003, 20.136999999999997, 20.091, 20.080000000000002, 20.070999999999998, 20.072, 20.073, 20.09, 20.095, 20.131, 20.070999999999998, 20.075, 20.072, 20.07, 20.077, 20.079, 20.084999999999997, 20.078, 20.092, 20.098000000000003, 20.087, 20.084999999999997, 20.149, 20.080000000000002, 20.080000000000002, 20.074, 20.079, 20.086, 20.079, 20.078, 20.078, 20.073, 20.076, 20.080000000000002, 20.074, 20.078, 20.074, 20.075, 20.088, 20.089, 20.086, 20.174999999999997, 20.198, 20.082, 20.076, 20.072, 20.078, 20.078, 20.089, 20.091, 20.082, 20.087, 20.082, 20.089, 20.099, 20.092, 20.084999999999997, 20.104, 20.067, 20.095, 20.098000000000003, 20.101999999999997, 20.084999999999997, 20.168, 20.075, 20.078, 20.072, 20.080000000000002, 20.076, 20.34, 20.087, 20.099, 20.076, 20.075, 20.067999999999998, 20.079, 20.079, 20.075, 20.076, 20.091, 20.098000000000003, 20.080000000000002, 20.075, 20.074, 20.149, 20.137999999999998, 20.074, 20.07, 20.131, 20.079, 20.073, 20.082, 20.067999999999998, 20.079, 20.077, 20.134, 20.067999999999998, 20.083, 20.084999999999997, 20.09, 20.076, 20.079, 20.084, 20.079, 20.077, 20.079, 20.075, 20.086, 20.069, 20.076, 20.077, 20.075, 20.073, 20.105, 20.074, 20.092, 20.080000000000002, 20.097, 20.101, 20.178, 20.076, 852.41, 20.157999999999998, 20.422, 20.439, 20.167, 20.14, 20.082, 20.097, 20.093, 20.069, 20.112000000000002, 20.074, 20.078, 20.062, 20.09, 20.064, 20.061, 20.064999999999998, 20.084, 20.061, 20.059, 20.097, 20.078, 20.087, 20.067999999999998, 20.064999999999998, 20.066, 20.066, 20.079, 20.070999999999998, 20.079, 20.064999999999998, 20.074, 20.069, 20.067999999999998, 20.062, 20.067, 20.081000000000003, 20.076, 20.060000000000002, 20.067, 20.075, 20.070999999999998, 20.066, 20.064999999999998, 20.072, 20.07, 20.076, 20.063000000000002, 20.060000000000002, 20.066, 20.81, 20.069, 20.064, 20.074, 20.061, 20.07, 20.059, 20.064, 20.072, 20.069, 20.072, 20.069, 20.079, 20.067, 20.07, 20.066, 20.069, 20.064999999999998, 20.07, 20.064, 20.064999999999998, 20.058, 20.060000000000002, 20.061, 20.064, 20.069, 20.057, 20.064, 20.058, 20.069, 40.455999999999996, 20.074, 20.062, 20.057, 20.056, 20.064999999999998, 20.122, 20.060000000000002, 20.057, 20.060000000000002, 20.059, 20.056, 20.058, 20.064, 20.062, 20.062, 20.060000000000002, 20.079, 20.063000000000002]
set_140 = [10.061, 49.342999999999996, 10.135, 10.095, 10.05, 20.194, 20.083, 20.118000000000002, 40.567, 20.061, 33.929, 20.084, 20.192, 20.183, 20.207, 20.168, 20.126, 20.119999999999997, 20.127, 20.115000000000002, 20.111, 20.113, 20.107, 20.11, 40.745000000000005, 20.108999999999998, 20.173, 43.295, 20.129, 20.079, 20.105, 20.074, 20.102999999999998, 20.165, 20.165, 20.077, 20.080000000000002, 20.187, 20.062, 20.066, 20.063000000000002, 20.062, 20.064999999999998, 20.081000000000003, 20.064999999999998, 20.084, 20.063000000000002, 20.063000000000002, 20.060000000000002, 20.061, 20.064999999999998, 23.85, 20.183, 20.069, 20.07, 20.063000000000002, 20.067, 20.064999999999998, 20.07, 20.064999999999998, 20.057, 20.062, 20.084999999999997, 20.182, 20.059, 20.069, 20.074, 20.067, 20.062, 20.07, 20.070999999999998, 20.127, 20.066, 20.129, 20.067, 20.119, 20.127, 20.072, 20.067999999999998, 20.070999999999998, 20.072, 20.073, 20.089, 20.111, 20.081000000000003, 20.086, 20.148, 20.107, 20.079, 20.075, 20.177, 20.070999999999998, 20.168, 20.207, 20.074, 20.133000000000003, 20.081000000000003, 20.101999999999997, 20.174, 20.097, 20.174, 20.137999999999998, 20.18, 20.115000000000002, 20.07, 20.081000000000003, 20.084, 20.164, 20.144, 20.223000000000003, 20.139, 20.16, 20.101, 20.153000000000002, 20.128, 20.18, 20.567, 20.188000000000002, 20.127, 20.186, 20.14, 20.153000000000002, 20.112000000000002, 20.157, 20.162, 20.173, 20.083, 20.151, 20.067999999999998, 20.166, 20.099, 20.163, 20.107, 20.076, 20.075, 20.096, 20.117, 20.088, 20.13, 20.133000000000003, 20.197, 20.101, 20.142, 20.075, 20.108, 20.093, 20.117, 20.072, 20.16, 20.078, 20.118000000000002, 20.116, 20.128, 20.079, 20.150000000000002, 21.187, 20.126, 20.114, 20.148, 20.069, 20.168, 25.625, 20.119999999999997, 20.081000000000003, 20.162, 20.399, 20.117, 31.357000000000003, 20.105, 20.154, 20.224, 20.159, 20.127, 20.156, 20.117, 20.172, 20.108, 20.139, 20.1, 20.139, 20.104, 20.17, 20.115000000000002, 20.137999999999998, 20.108999999999998, 24.511000000000003, 20.124, 20.181, 20.149, 24.505, 20.126, 20.19, 20.136000000000003, 20.225, 20.134, 20.163, 20.124, 20.19, 20.094, 20.147000000000002, 20.095, 20.172, 20.082, 20.154999999999998, 20.262999999999998, 20.154, 20.074, 20.159, 20.081000000000003, 20.287, 20.097, 20.347, 20.119, 20.294, 20.104, 20.156, 20.093, 20.18, 20.165, 20.149, 20.153000000000002, 20.154999999999998, 20.112000000000002, 20.156, 20.077, 20.136999999999997, 47.397, 20.136999999999997, 156.696, 20.744, 27.403, 20.078, 20.066, 20.069, 20.060000000000002, 20.069, 20.066, 20.075, 20.101999999999997, 20.067, 30.986, 20.07, 20.093, 20.063000000000002, 20.078, 20.084999999999997, 20.073, 20.135, 20.098000000000003, 20.105999999999998, 20.069, 20.067, 20.057, 20.066, 20.059, 20.067, 20.055, 20.060000000000002, 20.072, 20.124, 20.107, 20.062, 20.059, 20.069, 20.095, 20.115000000000002, 20.075, 20.066, 20.122, 20.059, 20.067, 20.07, 20.073, 20.074, 20.063000000000002, 20.064, 20.061, 20.056, 20.055, 20.053, 20.055, 20.057, 20.055, 20.054, 20.064999999999998, 20.058, 20.056, 20.052, 20.053, 20.058, 20.057, 20.054, 20.055, 20.058, 20.053, 20.053, 20.055, 20.070999999999998, 20.067, 20.060000000000002, 20.055, 20.056, 20.054, 20.054, 20.054, 20.057, 20.059, 20.119999999999997, 20.055, 20.056, 20.057, 20.061, 20.060000000000002, 20.060000000000002, 20.064999999999998, 20.059, 20.057, 20.055, 20.056, 20.057, 20.055, 20.059, 20.057, 20.075, 20.076, 20.060000000000002, 20.058, 20.11, 20.063000000000002, 20.062, 20.075, 20.074, 20.075, 20.075, 20.063000000000002, 20.063000000000002, 20.062, 20.064999999999998, 20.059, 20.059, 20.056, 20.059, 20.084]
set_120 = [22.412000000000003, 60.136, 22.711, 10.052999999999999, 11.533, 20.07, 20.122, 20.062, 20.075, 20.064999999999998, 20.063000000000002, 20.063000000000002, 20.066, 20.064999999999998, 20.174, 20.117, 24.561, 20.136000000000003, 22.949, 20.097, 20.189, 20.069, 20.142, 23.032, 20.134, 20.091, 20.097, 20.070999999999998, 20.062, 20.067, 20.067, 20.067, 20.066, 20.064999999999998, 20.061, 20.062, 20.061, 20.073, 20.226999999999997, 20.061, 20.075, 20.072, 20.057, 20.061, 20.059, 20.069, 20.064, 20.061, 20.067, 20.056, 20.060000000000002, 20.060000000000002, 20.062, 20.059, 20.058, 20.062, 20.062, 20.059, 20.061, 20.067, 20.060000000000002, 20.058, 20.059, 20.064999999999998, 20.059, 20.058, 20.059, 24.346, 20.058, 20.058, 20.062, 22.553, 23.531, 20.060000000000002, 20.057, 20.061, 20.061, 20.062, 20.058, 20.058, 20.063000000000002, 20.057, 20.055, 20.062, 20.059, 20.058, 20.058, 20.058, 20.057, 20.057, 20.060000000000002, 20.072, 24.409, 20.059, 20.072, 20.059, 20.063000000000002, 20.058, 20.058, 20.058, 20.055, 20.059, 20.059, 20.059, 20.058, 20.058, 20.056, 20.059, 20.057, 20.055, 20.058, 20.063000000000002, 20.059, 20.058, 24.368000000000002, 20.064999999999998, 20.060000000000002, 20.059, 20.057, 20.059, 20.057, 20.069, 20.061, 20.059, 20.062, 20.060000000000002, 20.059, 20.059, 20.058, 20.056, 20.058, 20.060000000000002, 20.058, 20.062, 20.059, 20.061, 20.059, 20.058, 20.059, 20.057, 20.056, 20.057, 20.057, 20.062, 20.059, 20.059, 20.058, 20.058, 20.057, 20.058, 20.058, 20.063000000000002, 20.060000000000002, 20.064999999999998, 20.067999999999998, 20.062, 20.060000000000002, 20.057, 25.035, 20.057, 20.056, 20.056, 24.784, 20.064999999999998, 20.153000000000002, 20.129, 24.241, 20.141, 20.060000000000002, 20.105, 23.812, 20.122999999999998, 20.102999999999998, 20.121, 23.298, 20.126, 20.062, 20.119999999999997, 22.762, 20.116, 20.112000000000002, 20.114, 22.264, 20.101, 20.069, 20.105999999999998, 21.496000000000002, 20.089, 20.059, 20.059, 21.195999999999998, 20.063000000000002, 20.058, 20.058, 20.88, 20.061, 20.059, 20.060000000000002, 20.556, 20.056, 20.055, 20.053, 20.342, 20.056, 20.060000000000002, 20.060000000000002, 20.064, 20.059, 20.070999999999998, 20.057, 20.057, 20.059, 20.057, 20.055, 20.060000000000002, 20.058, 20.060000000000002, 20.055, 20.058, 20.056, 20.056, 20.056, 20.056, 20.059, 20.057, 20.059, 20.057, 20.058, 20.056, 20.055, 20.057, 21.058, 20.087, 20.064, 20.061, 20.061, 20.063000000000002, 20.062, 20.066, 20.059, 20.061, 22.446, 20.064999999999998, 20.059, 20.064999999999998, 20.154999999999998, 25.395999999999997, 20.116, 20.105, 20.102999999999998, 20.066, 20.063000000000002, 20.058, 20.055, 20.064999999999998, 20.059, 20.057, 20.055, 20.057, 20.062, 20.056, 20.060000000000002, 20.075, 20.054, 20.059, 20.055, 20.056, 20.054, 20.133000000000003, 20.086, 20.064, 24.164, 20.059, 20.053, 20.060000000000002, 20.055, 20.055, 20.053, 20.054, 20.054, 20.087, 20.052, 20.056, 20.053, 20.055, 20.053, 20.055, 20.053, 20.055, 20.053, 20.055, 20.051, 20.058, 20.067999999999998, 20.057, 20.055, 20.054, 20.066, 20.056, 20.055, 20.054, 20.059, 20.054, 20.053, 20.056, 20.054, 20.053, 20.053, 20.053, 20.056, 20.057, 20.058, 20.058, 20.061, 20.058, 20.066, 20.062, 20.059, 20.060000000000002, 20.060000000000002, 20.060000000000002, 20.063000000000002, 20.061, 20.064, 20.070999999999998, 20.064, 20.063000000000002, 20.062, 20.063000000000002, 20.080000000000002, 20.060000000000002, 20.060000000000002, 20.079, 25.319000000000003, 23.516, 20.066, 20.07, 20.064999999999998, 20.058, 20.053, 20.064, 20.084999999999997, 20.07]
data_to_plot = [set_180, set_160, set_140, set_120]

fig = plt.figure(1, figsize(9,6))
ax = fig.add_subplot(111)
bp = ax.boxplot(data_to_plot)