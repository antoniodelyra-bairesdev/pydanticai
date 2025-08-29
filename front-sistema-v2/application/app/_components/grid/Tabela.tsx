import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import "ag-grid-enterprise";
import "./Tabela.css";
import { AgGridReact, AgGridReactProps } from "ag-grid-react";
import { Box, BoxProps } from "@chakra-ui/react";

export type TabelaProps = {
  boxProps?: BoxProps;
  gridProps?: AgGridReactProps;
};

export function Tabela({ boxProps, gridProps }: TabelaProps) {
  return (
    <Box className="ag-theme-alpine" {...boxProps}>
      <AgGridReact
        defaultColDef={{
          sortable: true,
          filter: true,
        }}
        enableRangeSelection
        {...gridProps}
      />
    </Box>
  );
}
