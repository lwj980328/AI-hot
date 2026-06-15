import axios from "axios";

/** Axios 实例 - 用于后端 API 通信 */
const apiClient = axios.create({
  baseURL: "/api/v1",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 响应拦截器：统一处理 ApiResponse
apiClient.interceptors.response.use(
  (response) => {
    // 提取 ApiResponse.data 字段
    const apiResponse = response.data;
    if (apiResponse && typeof apiResponse === "object" && "success" in apiResponse) {
      if (!apiResponse.success) {
        // API 返回错误
        return Promise.reject(new Error(apiResponse.message || "请求失败"));
      }
      // 替换 response.data 为实际数据
      response.data = apiResponse.data;
    }
    return response;
  },
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;
