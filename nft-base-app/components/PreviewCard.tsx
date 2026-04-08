import Image from "next/image";
import type { GenerateResult } from "@/lib/api";

interface Props {
  result: GenerateResult;
}

/**
 * PreviewCard – displays the generated NFT image and its trait attributes.
 */
export function PreviewCard({ result }: Props) {
  const { imageUrl, attributes } = result;

  return (
    <div style={styles.card}>
      <div style={styles.imageWrapper}>
        <Image
          src={imageUrl}
          alt="Generated NFT preview"
          width={320}
          height={320}
          style={styles.image}
          unoptimized={imageUrl.startsWith("http")}
        />
      </div>

      {attributes.length > 0 && (
        <div style={styles.attributes}>
          <h3 style={styles.attrsTitle}>Traits</h3>
          <div style={styles.attrsGrid}>
            {attributes.map((attr) => (
              <div key={attr.trait_type} style={styles.attr}>
                <span style={styles.attrLabel}>{attr.trait_type}</span>
                <span style={styles.attrValue}>{attr.value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  card: {
    border: "1px solid #e0e0e0",
    borderRadius: "12px",
    overflow: "hidden",
    background: "#fff",
    maxWidth: "360px",
    margin: "0 auto",
    boxShadow: "0 2px 12px rgba(0,0,0,0.06)",
  },
  imageWrapper: {
    width: "100%",
    aspectRatio: "1",
    position: "relative" as const,
    background: "#f0f0f0",
  },
  image: {
    width: "100%",
    height: "auto",
    display: "block",
  },
  attributes: {
    padding: "16px",
  },
  attrsTitle: {
    margin: "0 0 10px",
    fontSize: "0.95rem",
    fontWeight: 700,
    color: "#333",
  },
  attrsGrid: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "8px",
  },
  attr: {
    background: "#f5f7ff",
    borderRadius: "8px",
    padding: "8px 10px",
    display: "flex",
    flexDirection: "column" as const,
    gap: "2px",
  },
  attrLabel: {
    fontSize: "0.7rem",
    color: "#0052ff",
    fontWeight: 600,
    textTransform: "uppercase" as const,
    letterSpacing: "0.04em",
  },
  attrValue: {
    fontSize: "0.9rem",
    fontWeight: 600,
    color: "#111",
  },
};
