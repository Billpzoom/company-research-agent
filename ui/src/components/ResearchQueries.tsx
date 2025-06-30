import React from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import type { ResearchQueriesProps } from '../types';

type Query = ResearchQueriesProps['queries'][0];
type StreamingQuery = ResearchQueriesProps['streamingQueries'][string];

/**
 * 查询类别定义
 */
type Category = {
  key: 'company' | 'industry' | 'financial' | 'news';
  label: string;
};

/**
 * 流式查询卡片组件
 */
const StreamingQueryCard: React.FC<{
  query: StreamingQuery & { text: string };
  className: string;
}> = ({ query, className }) => (
  <div className={className}>
    <span className="text-gray-600">{query.text}</span>
    {/* 添加闪烁光标效果表示正在生成 */}
    <span className="animate-pulse ml-1 text-[#8FBCFA]">|</span>
  </div>
);

/**
 * 已完成查询卡片组件
 */
const CompletedQueryCard: React.FC<{
  query: Query & { category?: string };
  className: string;
}> = ({ query, className }) => (
  <div className={className}>
    <span className="text-gray-600">{query.text}</span>
  </div>
);

/**
 * 查询类别组件
 */
const QueryCategory: React.FC<{
  category: Category;
  streamingQueries: Record<string, StreamingQuery>;
  queries: Array<Query & { category: string }>;
  glassStyle: string;
  streamingQueryCardStyle: string;
  completedQueryCardStyle: string;
}> = ({ 
  category, 
  streamingQueries, 
  queries, 
  glassStyle,
  streamingQueryCardStyle,
  completedQueryCardStyle
}) => {
  const { key, label } = category;
  
  return (
    <div className={`${glassStyle} rounded-xl p-3`}>
      <h3 className="text-base font-medium text-gray-900 mb-3">
        {label}查询
      </h3>
      <div className="space-y-2">
        {/* 优先显示正在流式传输的查询 */}
        {Object.entries(streamingQueries)
          .filter(([queryKey]) => queryKey.startsWith(key))
          .map(([key, query]) => (
            <StreamingQueryCard
              key={key}
              query={query}
              className={streamingQueryCardStyle}
            />
          ))}
        {/* 然后显示已完成的查询 */}
        {queries
          .filter((q) => q.category.startsWith(key))
          .map((query, idx) => (
            <CompletedQueryCard
              key={idx}
              query={query}
              className={completedQueryCardStyle}
            />
          ))}
      </div>
    </div>
  );
};


/**
 * ResearchQueries组件
 * 
 * 用于展示和管理研究查询列表的可折叠组件。支持实时查询流和已完成查询的展示，
 * 并按类别（公司、行业、财务、新闻）对查询进行分组显示。
 * 
 * @param queries - 已完成的查询列表
 * @param streamingQueries - 正在进行的实时查询
 * @param isExpanded - 控制组件是否展开
 * @param onToggleExpand - 切换展开/折叠状态的回调函数
 * @param isResetting - 是否正在重置状态（用于动画效果）
 * @param glassStyle - 毛玻璃效果的样式类名
 */
const ResearchQueries: React.FC<ResearchQueriesProps> = ({
  queries,
  streamingQueries,
  isExpanded,
  onToggleExpand,
  isResetting,
  glassStyle
}) => {
  // 定义基础样式常量
  const glassCardStyle = `${glassStyle} rounded-2xl p-6`;
  const fadeInAnimation = "transition-all duration-300 ease-in-out";
  
  // 查询卡片样式
  const queryCardStyle = "backdrop-filter backdrop-blur-lg bg-white/80 border rounded-lg p-2";
  const streamingQueryCardStyle = `${queryCardStyle} border-[#468BFF]/30`; // 流式查询带有蓝色边框
  const completedQueryCardStyle = `${queryCardStyle} border-gray-200`;      // 已完成查询带有灰色边框
  
  // 查询类别定义
  const categories = [
    { key: 'company', label: '公司' },
    { key: 'industry', label: '行业' },
    { key: 'financial', label: '财务' },
    { key: 'news', label: '新闻' }
  ] as const;

  // 定义组件的主要样式
  const containerStyle = `${glassCardStyle} ${fadeInAnimation} ${isResetting ? 'opacity-0 transform -translate-y-4' : 'opacity-100 transform translate-y-0'} font-['DM_Sans']`;
  const headerStyle = "flex items-center justify-between cursor-pointer";
  const titleStyle = "text-xl font-semibold text-gray-900";
  const toggleButtonStyle = "text-gray-600 hover:text-gray-900 transition-colors";
  
  // 内容区域样式，根据展开状态动态调整高度和透明度
  const contentStyle = `overflow-hidden transition-all duration-500 ease-in-out ${
    isExpanded ? 'mt-4 max-h-[1000px] opacity-100' : 'max-h-0 opacity-0'
  }`;
  
  return (
    <div className={containerStyle}>
      <div 
        className={headerStyle}
        onClick={onToggleExpand}
      >
        <h2 className={titleStyle}>
          生成的研究查询
        </h2>
        <button className={toggleButtonStyle}>
          {isExpanded ? (
            <ChevronUp className="h-6 w-6" />
          ) : (
            <ChevronDown className="h-6 w-6" />
          )}
        </button>
      </div>
      
      <div className={contentStyle}>
        {/* 使用网格布局展示查询类别 */}
        <div className="grid grid-cols-2 gap-4">
          {categories.map((category) => (
            <QueryCategory
              key={category.key}
              category={category}
              streamingQueries={streamingQueries}
              queries={queries}
              glassStyle={glassStyle}
              streamingQueryCardStyle={streamingQueryCardStyle}
              completedQueryCardStyle={completedQueryCardStyle}
            />
          ))}
        </div>
      </div>
      
      {/* 当组件折叠时显示查询统计信息 */}
      {!isExpanded && (
        <div className="mt-2 text-sm text-gray-600">
          {queries.length} 个查询生成于 {categories.length} 个类别
        </div>
      )}
    </div>
  );
};

export default ResearchQueries; 