import { apiClient } from "./client";
import {
  ImageUploadResponse,
  Lot,
  LotCreatePayload,
  LotImage,
  LotStatus,
  Order,
} from "../types";

export interface TakeLotResponse {
  claim_code: string;
  order: Order;
}

export const createLot = async (payload: LotCreatePayload): Promise<Lot> => {
  const response = await apiClient.post<Lot>("/lots", payload);
  return response.data;
};

export const uploadLotImage = async (file: File): Promise<ImageUploadResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  const response = await apiClient.post<ImageUploadResponse>(
    "/lots/upload-image",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
  return response.data;
};

export const addLotImage = async (
  lotId: string,
  file: File,
  displayOrder: number = 0,
  caption?: string
): Promise<LotImage> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("display_order", String(displayOrder));
  if (caption) {
    formData.append("caption", caption);
  }
  const response = await apiClient.post<LotImage>(
    `/lots/${lotId}/images`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
  return response.data;
};

export const getLot = async (id: string): Promise<Lot> => {
  const response = await apiClient.get<Lot>(`/lots/${id}`);
  return response.data;
};

export const listLots = async (status?: LotStatus): Promise<Lot[]> => {
  const response = await apiClient.get<Lot[]>("/lots", {
    params: status ? { status } : undefined,
  });
  return response.data;
};

export const takeLot = async (
  lotId: string,
  payload?: {
    buyer_contact?: string;
    shipping_address?: Record<string, unknown>;
    payment_reference?: string;
  }
): Promise<TakeLotResponse> => {
  const response = await apiClient.post<TakeLotResponse>(
    `/lots/${lotId}/take`,
    payload ?? {}
  );
  return response.data;
};
