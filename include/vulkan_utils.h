#ifndef VULKAN_UTILS_H
#define VULKAN_UTILS_H

#include <vulkan/vulkan.h>
#include <vector>
#include <string>
#include <stdexcept>

namespace VkUtils {
    std::vector<char> readShaderFile(const std::string& filename);
    VkShaderModule createShaderModule(VkDevice device, const std::vector<char>& code);
    uint32_t findMemoryType(VkPhysicalDevice physicalDevice, uint32_t typeFilter, VkMemoryPropertyFlags properties);
    void createBuffer(VkDevice device, VkPhysicalDevice physicalDevice,
                      VkDeviceSize size, VkBufferUsageFlags usage, 
                      VkMemoryPropertyFlags properties, VkBuffer& buffer, VkDeviceMemory& memory);
    void copyToBuffer(VkDevice device, VkBuffer dstBuffer, VkDeviceSize size, const void* data);
}

#endif // VULKAN_UTILS_H
