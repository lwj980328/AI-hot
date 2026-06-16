import { useState } from "react";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface MemorySearchProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

/** 语义搜索组件 */
export function MemorySearch({
  onSearch,
  placeholder = "搜索记忆... (语义搜索)",
}: MemorySearchProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleClear = () => {
    setQuery("");
    onSearch("");
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        className="pl-10 pr-20"
      />
      <div className="absolute right-2 top-1/2 flex -translate-y-1/2 gap-1">
        {query && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-7 w-7 p-0"
            onClick={handleClear}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
        <Button type="submit" size="sm" className="h-7" disabled={!query.trim()}>
          搜索
        </Button>
      </div>
    </form>
  );
}
