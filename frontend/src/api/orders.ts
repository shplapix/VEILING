import { apiClient } from "./client";
import { Order } from "../types";

export const lookupOrder = async (code: string): Promise<Order> => {
  const response = await apiClient.get<Order>("/orders/lookup", {
    params: { code: code.trim().toUpperCase() },
  });
  return response.data;
};

export const getLedger = async (): Promise<Order[]> => {
  const response = await apiClient.get<Order[]>("/orders/ledger");
  return response.data;
};
